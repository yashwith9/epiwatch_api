"""
EpiWatch Data Ingestion Configuration

Configuration management for data collection services.
Handles RSS feeds, news APIs, and social media sources.

Author: EpiWatch Team
License: MIT
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RSSSource:
    """RSS feed source configuration"""
    name: str
    url: str
    language: str = "en"
    region: str = "global"
    priority: int = 1
    enabled: bool = True


@dataclass
class APIConfig:
    """API configuration for external services"""
    name: str
    base_url: str
    api_key: str
    rate_limit: int = 100
    timeout: int = 30
    enabled: bool = True


class IngestionConfig:
    """Main configuration class for data ingestion"""
    
    def __init__(self):
        # RSS Feed Sources
        self.rss_sources = [
            RSSSource("WHO Disease Outbreaks", "https://www.who.int/feeds/entity/disease-outbreak-news/rss.xml"),
            RSSSource("CDC Health Alerts", "https://tools.cdc.gov/api/v2/resources/media/rss.xml"),
            RSSSource("ProMED", "https://promedmail.org/rss/"),
            RSSSource("ECDC", "https://www.ecdc.europa.eu/en/news-events/rss.xml"),
            RSSSource("Reuters Health", "http://feeds.reuters.com/reuters/healthNews"),
            RSSSource("BBC Health", "http://feeds.bbci.co.uk/news/health/rss.xml"),
            RSSSource("CNN Health", "http://rss.cnn.com/rss/edition.rss"),
        ]
        
        # API Configurations
        self.api_configs = {
            "newsapi": APIConfig(
                name="NewsAPI",
                base_url="https://newsapi.org/v2",
                api_key=os.getenv("NEWS_API_KEY", ""),
                rate_limit=500,
                timeout=30
            ),
            "gdelt": APIConfig(
                name="GDELT",
                base_url="https://api.gdeltproject.org/api/v2",
                api_key=os.getenv("GDELT_API_KEY", ""),
                rate_limit=1000,
                timeout=45
            )
        }
        
        # Database Configuration
        self.database_url = os.getenv("DATABASE_URL")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # Processing Settings
        self.batch_size = int(os.getenv("INGESTION_BATCH_SIZE", "100"))
        self.collection_interval = int(os.getenv("COLLECTION_INTERVAL_MINUTES", "15"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY_SECONDS", "60"))
        
        # Content Filtering
        self.min_content_length = int(os.getenv("MIN_CONTENT_LENGTH", "100"))
        self.max_content_age_days = int(os.getenv("MAX_CONTENT_AGE_DAYS", "7"))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("INGESTION_LOG_FILE", "logs/ingestion.log")
    
    def get_enabled_rss_sources(self) -> List[RSSSource]:
        """Get list of enabled RSS sources"""
        return [source for source in self.rss_sources if source.enabled]
    
    def get_enabled_apis(self) -> Dict[str, APIConfig]:
        """Get enabled API configurations"""
        return {name: config for name, config in self.api_configs.items() 
                if config.enabled and config.api_key}
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.database_url:
            errors.append("DATABASE_URL is required")
            
        if not self.redis_url:
            errors.append("REDIS_URL is required")
            
        # Check API keys for enabled services
        for name, config in self.api_configs.items():
            if config.enabled and not config.api_key:
                errors.append(f"{name} API key is missing")
        
        return errors


# Global configuration instance
config = IngestionConfig()