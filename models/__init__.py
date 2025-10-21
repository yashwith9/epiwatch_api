"""
EpiWatch Models Module

Handles forecasting and anomaly detection:
- Time series forecasting with Prophet
- Anomaly detection algorithms
- Alert generation and scoring
- Model training and evaluation

Author: EpiWatch Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "EpiWatch Team"

from .forecasting import ProphetForecaster, TimeSeriesAnalyzer
from .anomaly import AnomalyDetector, OutbreakScorer
from .alerts import AlertGenerator, SeverityCalculator

__all__ = [
    "ProphetForecaster",
    "TimeSeriesAnalyzer",
    "AnomalyDetector", 
    "OutbreakScorer",
    "AlertGenerator",
    "SeverityCalculator"
]