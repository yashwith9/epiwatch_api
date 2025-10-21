"""
EpiWatch RSS and News Data Collectors

Handles data collection from RSS feeds, news APIs, and social media sources.
Implements rate limiting, retry logic, and content validation.

Author: EpiWatch Team
License: MIT
"""

import asyncio
import aiohttp
import feedparser
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin
import hashlib
import json

from .config import config
from .processors import TextCleaner, ContentValidator
from .storage import RedisQueue, DatabaseStorage


@dataclass
class Article:
    """Article data structure"""
    id: str
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    language: str = "en"
    region: str = "global"
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
        if self.raw_data is None:
            self.raw_data = {}
    
    def _generate_id(self) -> str:
        """Generate unique ID from URL and title"""
        content = f"{self.url}_{self.title}_{self.published_at}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['published_at'] = self.published_at.isoformat()
        return data


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < 60]
        
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.calls.append(now)


class RSSCollector:
    """RSS feed collector with async processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_cleaner = TextCleaner()
        self.validator = ContentValidator()
        self.rate_limiter = RateLimiter(calls_per_minute=30)  # Conservative rate
        
    async def collect_from_source(self, rss_source) -> List[Article]:
        """Collect articles from a single RSS source"""
        await self.rate_limiter.wait_if_needed()
        
        try:
            self.logger.info(f"Collecting from RSS source: {rss_source.name}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(rss_source.url, timeout=30) as response:
                    content = await response.text()
                    
            feed = feedparser.parse(content)
            articles = []
            
            for entry in feed.entries:
                try:
                    article = self._parse_rss_entry(entry, rss_source)
                    if article and self.validator.is_valid_article(article):
                        articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Failed to parse entry: {e}")
                    
            self.logger.info(f"Collected {len(articles)} articles from {rss_source.name}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to collect from {rss_source.name}: {e}")
            return []
    
    def _parse_rss_entry(self, entry, rss_source) -> Optional[Article]:
        """Parse RSS entry into Article object"""
        try:
            # Extract published date
            published_at = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6])
            
            # Skip old articles
            cutoff_date = datetime.now() - timedelta(days=config.max_content_age_days)
            if published_at < cutoff_date:
                return None
            
            # Clean content
            title = self.text_cleaner.clean_text(entry.get('title', ''))
            content = self.text_cleaner.clean_text(
                entry.get('description', '') or entry.get('summary', '')
            )
            
            # Skip if content too short
            if len(content) < config.min_content_length:
                return None
            
            return Article(
                id="",  # Will be generated in __post_init__
                title=title,
                content=content,
                url=entry.get('link', ''),
                source=rss_source.name,
                published_at=published_at,
                language=rss_source.language,
                region=rss_source.region,
                raw_data={'entry': dict(entry)}
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse RSS entry: {e}")
            return None
    
    async def collect_all_sources(self) -> List[Article]:
        """Collect from all enabled RSS sources"""
        sources = config.get_enabled_rss_sources()
        tasks = [self.collect_from_source(source) for source in sources]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            else:
                self.logger.error(f"Collection task failed: {result}")
        
        return all_articles


class NewsAPICollector:
    """NewsAPI collector for health-related news"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_cleaner = TextCleaner()
        self.validator = ContentValidator()
        
        api_config = config.api_configs.get("newsapi")
        if not api_config or not api_config.enabled:
            raise ValueError("NewsAPI configuration not found or disabled")
            
        self.api_key = api_config.api_key
        self.base_url = api_config.base_url
        self.rate_limiter = RateLimiter(calls_per_minute=api_config.rate_limit)
    
    async def collect_health_news(self, 
                                  query: str = "disease outbreak epidemic pandemic", 
                                  days_back: int = 1) -> List[Article]:
        """Collect health-related news articles"""
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.api_key,
                'pageSize': 100
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/everything"
                async with session.get(url, params=params, timeout=30) as response:
                    data = await response.json()
            
            if data.get('status') != 'ok':
                self.logger.error(f"NewsAPI error: {data.get('message')}")
                return []
            
            articles = []
            for item in data.get('articles', []):
                article = self._parse_newsapi_article(item)
                if article and self.validator.is_valid_article(article):
                    articles.append(article)
            
            self.logger.info(f"Collected {len(articles)} articles from NewsAPI")
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to collect from NewsAPI: {e}")
            return []
    
    def _parse_newsapi_article(self, item: Dict[str, Any]) -> Optional[Article]:
        """Parse NewsAPI article into Article object"""
        try:
            # Parse published date
            published_str = item.get('publishedAt', '')
            published_at = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            
            # Clean content
            title = self.text_cleaner.clean_text(item.get('title', ''))
            content = self.text_cleaner.clean_text(
                item.get('description', '') + " " + item.get('content', '')
            )
            
            # Skip if content too short
            if len(content) < config.min_content_length:
                return None
            
            return Article(
                id="",
                title=title,
                content=content,
                url=item.get('url', ''),
                source=f"NewsAPI - {item.get('source', {}).get('name', 'Unknown')}",
                published_at=published_at,
                language="en",
                region="global",
                raw_data={'newsapi_item': item}
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse NewsAPI article: {e}")
            return None


class TwitterCollector:
    """Twitter/X collector for health-related tweets (placeholder)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Note: Twitter API requires proper authentication setup
        # This is a placeholder for future implementation
        
    async def collect_health_tweets(self, query: str = "#outbreak OR #epidemic OR #pandemic") -> List[Article]:
        """Collect health-related tweets"""
        self.logger.info("Twitter collection not implemented yet")
        return []


class DataIngestionOrchestrator:
    """Main orchestrator for data ingestion pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rss_collector = RSSCollector()
        self.redis_queue = RedisQueue()
        self.db_storage = DatabaseStorage()
        
        # Initialize API collectors if available
        self.collectors = {}
        
        if config.api_configs.get("newsapi", {}).enabled:
            try:
                self.collectors["newsapi"] = NewsAPICollector()
            except ValueError as e:
                self.logger.warning(f"NewsAPI collector disabled: {e}")
        
        self.collectors["twitter"] = TwitterCollector()  # Always available (placeholder)
    
    async def run_collection_cycle(self) -> Dict[str, int]:
        """Run one complete collection cycle"""
        start_time = time.time()
        stats = {"total_articles": 0, "sources": 0, "errors": 0}
        
        self.logger.info("Starting data collection cycle")
        
        # Collect from RSS sources
        try:
            rss_articles = await self.rss_collector.collect_all_sources()
            await self._process_articles(rss_articles)
            stats["total_articles"] += len(rss_articles)
            stats["sources"] += 1
        except Exception as e:
            self.logger.error(f"RSS collection failed: {e}")
            stats["errors"] += 1
        
        # Collect from API sources
        for name, collector in self.collectors.items():
            try:
                if name == "newsapi":
                    articles = await collector.collect_health_news()
                elif name == "twitter":
                    articles = await collector.collect_health_tweets()
                else:
                    continue
                    
                await self._process_articles(articles)
                stats["total_articles"] += len(articles)
                stats["sources"] += 1
                
            except Exception as e:
                self.logger.error(f"{name} collection failed: {e}")
                stats["errors"] += 1
        
        duration = time.time() - start_time
        self.logger.info(f"Collection cycle completed in {duration:.2f}s: {stats}")
        
        return stats
    
    async def _process_articles(self, articles: List[Article]):
        """Process articles: store in database and queue for NLP"""
        if not articles:
            return
        
        # Store in database
        await self.db_storage.store_articles(articles)
        
        # Queue for NLP processing
        for article in articles:
            await self.redis_queue.push_for_nlp(article.to_dict())
    
    async def run_continuous_collection(self):
        """Run continuous collection with configurable intervals"""
        interval_minutes = config.collection_interval
        
        self.logger.info(f"Starting continuous collection (interval: {interval_minutes} minutes)")
        
        while True:
            try:
                await self.run_collection_cycle()
                await asyncio.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                self.logger.info("Collection stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in collection cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying