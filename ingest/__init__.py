"""
EpiWatch Data Ingestion Module

This module handles real-time data collection from various sources:
- RSS feeds
- News APIs (GDELT, NewsAPI)
- Social media (Twitter, Reddit)
- Web scraping

Author: EpiWatch Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "EpiWatch Team"

from .collectors import RSSCollector, NewsAPICollector, TwitterCollector
from .processors import TextCleaner, ContentValidator
from .storage import RedisQueue, DatabaseStorage

__all__ = [
    "RSSCollector",
    "NewsAPICollector", 
    "TwitterCollector",
    "TextCleaner",
    "ContentValidator",
    "RedisQueue",
    "DatabaseStorage"
]