"""
EpiWatch ETL Module

Handles Extract, Transform, Load operations:
- Data aggregation by disease and location
- Rolling window calculations
- Database operations
- Data quality monitoring

Author: EpiWatch Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "EpiWatch Team"

from .aggregators import DailyAggregator, WeeklyAggregator
from .transformers import RollingWindowCalculator, DataNormalizer
from .loaders import DatabaseLoader, CacheUpdater

__all__ = [
    "DailyAggregator",
    "WeeklyAggregator",
    "RollingWindowCalculator",
    "DataNormalizer", 
    "DatabaseLoader",
    "CacheUpdater"
]