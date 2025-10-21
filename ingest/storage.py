"""
EpiWatch Storage Components

Handles Redis queue operations and database storage
for the data ingestion pipeline.

Author: EpiWatch Team
License: MIT
"""

import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import redis.asyncio as redis
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from .config import config


# Database Models
Base = declarative_base()


class RawArticle(Base):
    """Raw article storage model"""
    __tablename__ = "raw_articles"
    
    id = sa.Column(sa.String, primary_key=True)
    title = sa.Column(sa.Text, nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    url = sa.Column(sa.String, nullable=False, unique=True)
    source = sa.Column(sa.String, nullable=False)
    published_at = sa.Column(sa.DateTime, nullable=False)
    collected_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    language = sa.Column(sa.String, default="en")
    region = sa.Column(sa.String, default="global")
    raw_data = sa.Column(JSONB, nullable=True)
    processing_status = sa.Column(sa.String, default="pending")  # pending, processing, completed, failed
    quality_score = sa.Column(sa.Float, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        sa.Index('idx_raw_articles_published_at', 'published_at'),
        sa.Index('idx_raw_articles_source', 'source'),
        sa.Index('idx_raw_articles_status', 'processing_status'),
        sa.Index('idx_raw_articles_collected_at', 'collected_at'),
    )


class IngestionStats(Base):
    """Ingestion statistics tracking"""
    __tablename__ = "ingestion_stats"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = sa.Column(sa.DateTime, default=datetime.utcnow)
    source_name = sa.Column(sa.String, nullable=False)
    articles_collected = sa.Column(sa.Integer, default=0)
    articles_valid = sa.Column(sa.Integer, default=0)
    articles_duplicate = sa.Column(sa.Integer, default=0)
    collection_duration_seconds = sa.Column(sa.Float)
    error_count = sa.Column(sa.Integer, default=0)
    error_details = sa.Column(JSONB, nullable=True)


class RedisQueue:
    """Redis-based queue for inter-service communication"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.redis_client = None
        self.nlp_queue = "epiwatch:nlp_queue"
        self.processing_queue = "epiwatch:processing_queue"
        self.alerts_queue = "epiwatch:alerts_queue"
    
    async def _get_redis_client(self):
        """Get Redis client with connection pooling"""
        if not self.redis_client:
            self.redis_client = redis.from_url(
                config.redis_url,
                decode_responses=True,
                max_connections=20
            )
        return self.redis_client
    
    async def push_for_nlp(self, article_data: Dict[str, Any]) -> bool:
        """Push article to NLP processing queue"""
        try:
            client = await self._get_redis_client()
            
            # Add metadata
            queue_item = {
                'article_data': article_data,
                'queued_at': datetime.utcnow().isoformat(),
                'priority': self._calculate_priority(article_data),
                'retry_count': 0
            }
            
            # Push to queue (use LPUSH for FIFO with RPOP)
            await client.lpush(self.nlp_queue, json.dumps(queue_item))
            
            self.logger.debug(f"Queued article for NLP: {article_data.get('id', 'unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue article for NLP: {e}")
            return False
    
    async def pop_for_nlp(self, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Pop article from NLP queue (blocking)"""
        try:
            client = await self._get_redis_client()
            
            # Blocking pop with timeout
            result = await client.brpop(self.nlp_queue, timeout=timeout)
            
            if result:
                queue_name, item_json = result
                return json.loads(item_json)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to pop from NLP queue: {e}")
            return None
    
    async def push_for_processing(self, nlp_result: Dict[str, Any]) -> bool:
        """Push NLP results to processing queue"""
        try:
            client = await self._get_redis_client()
            
            queue_item = {
                'nlp_result': nlp_result,
                'queued_at': datetime.utcnow().isoformat(),
                'retry_count': 0
            }
            
            await client.lpush(self.processing_queue, json.dumps(queue_item))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue NLP result for processing: {e}")
            return False
    
    async def push_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Push alert to alerts queue"""
        try:
            client = await self._get_redis_client()
            
            alert_item = {
                'alert_data': alert_data,
                'created_at': datetime.utcnow().isoformat(),
                'priority': alert_data.get('severity', 0.5)
            }
            
            await client.lpush(self.alerts_queue, json.dumps(alert_item))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue alert: {e}")
            return False
    
    def _calculate_priority(self, article_data: Dict[str, Any]) -> float:
        """Calculate processing priority for article"""
        priority = 0.5  # Default priority
        
        # Boost priority for recent articles
        try:
            published_at = datetime.fromisoformat(article_data.get('published_at', ''))
            hours_old = (datetime.utcnow() - published_at).total_seconds() / 3600
            
            if hours_old <= 1:
                priority += 0.3
            elif hours_old <= 6:
                priority += 0.2
            elif hours_old <= 24:
                priority += 0.1
        except:
            pass
        
        # Boost priority for credible sources
        source = article_data.get('source', '').lower()
        if any(credible in source for credible in ['who', 'cdc', 'reuters', 'bbc']):
            priority += 0.2
        
        # Boost priority for urgent keywords
        title = article_data.get('title', '').lower()
        content = article_data.get('content', '').lower()
        
        urgent_keywords = ['outbreak', 'epidemic', 'pandemic', 'emergency', 'alert']
        if any(keyword in title or keyword in content for keyword in urgent_keywords):
            priority += 0.1
        
        return min(priority, 1.0)
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get current queue statistics"""
        try:
            client = await self._get_redis_client()
            
            stats = {}
            stats['nlp_queue_size'] = await client.llen(self.nlp_queue)
            stats['processing_queue_size'] = await client.llen(self.processing_queue)
            stats['alerts_queue_size'] = await client.llen(self.alerts_queue)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get queue stats: {e}")
            return {}
    
    async def clear_queues(self):
        """Clear all queues (for testing/maintenance)"""
        try:
            client = await self._get_redis_client()
            
            await client.delete(self.nlp_queue)
            await client.delete(self.processing_queue)
            await client.delete(self.alerts_queue)
            
            self.logger.info("All queues cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear queues: {e}")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()


class DatabaseStorage:
    """Async database storage for articles and statistics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine = None
        self.async_session = None
    
    async def _get_engine(self):
        """Get async database engine"""
        if not self.engine:
            # Convert sync PostgreSQL URL to async
            db_url = config.database_url
            if db_url.startswith('postgresql://'):
                db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
            elif not db_url.startswith('postgresql+asyncpg://'):
                raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
            
            self.engine = create_async_engine(
                db_url,
                echo=False,  # Set to True for SQL debugging
                pool_size=10,
                max_overflow=20
            )
            
            # Create session factory
            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        
        return self.engine
    
    async def initialize_database(self):
        """Create database tables"""
        engine = await self._get_engine()
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        self.logger.info("Database tables initialized")
    
    async def store_articles(self, articles: List) -> Dict[str, int]:
        """Store articles in database"""
        if not articles:
            return {'stored': 0, 'duplicates': 0, 'errors': 0}
        
        stats = {'stored': 0, 'duplicates': 0, 'errors': 0}
        
        try:
            engine = await self._get_engine()
            
            async with self.async_session() as session:
                for article in articles:
                    try:
                        # Check for existing article by URL
                        result = await session.execute(
                            sa.select(RawArticle).where(RawArticle.url == article.url)
                        )
                        existing = result.scalars().first()
                        
                        if existing:
                            stats['duplicates'] += 1
                            continue
                        
                        # Create new article record
                        db_article = RawArticle(
                            id=article.id,
                            title=article.title,
                            content=article.content,
                            url=article.url,
                            source=article.source,
                            published_at=article.published_at,
                            language=article.language,
                            region=article.region,
                            raw_data=article.raw_data,
                            processing_status="pending"
                        )
                        
                        session.add(db_article)
                        stats['stored'] += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to store article {article.id}: {e}")
                        stats['errors'] += 1
                
                # Commit all changes
                await session.commit()
            
            self.logger.info(f"Stored articles - {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Database storage failed: {e}")
            return {'stored': 0, 'duplicates': 0, 'errors': len(articles)}
    
    async def update_processing_status(self, article_id: str, status: str, 
                                     quality_score: Optional[float] = None):
        """Update article processing status"""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    sa.select(RawArticle).where(RawArticle.id == article_id)
                )
                article = result.scalars().first()
                
                if article:
                    article.processing_status = status
                    if quality_score is not None:
                        article.quality_score = quality_score
                    
                    await session.commit()
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update processing status: {e}")
            return False
    
    async def store_ingestion_stats(self, stats_data: Dict[str, Any]) -> bool:
        """Store ingestion statistics"""
        try:
            async with self.async_session() as session:
                stats_record = IngestionStats(**stats_data)
                session.add(stats_record)
                await session.commit()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store ingestion stats: {e}")
            return False
    
    async def get_pending_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get articles pending NLP processing"""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    sa.select(RawArticle)
                    .where(RawArticle.processing_status == "pending")
                    .order_by(RawArticle.collected_at.desc())
                    .limit(limit)
                )
                
                articles = result.scalars().all()
                
                return [
                    {
                        'id': article.id,
                        'title': article.title,
                        'content': article.content,
                        'url': article.url,
                        'source': article.source,
                        'published_at': article.published_at.isoformat(),
                        'language': article.language,
                        'region': article.region
                    }
                    for article in articles
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get pending articles: {e}")
            return []
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()