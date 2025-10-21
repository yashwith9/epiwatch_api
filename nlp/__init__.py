"""
EpiWatch NLP Module

Handles natural language processing for disease outbreak detection:
- Disease name extraction with fuzzy matching
- Location extraction and geocoding
- Confidence scoring
- Text preprocessing and normalization

Author: EpiWatch Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "EpiWatch Team"

from .extractors import DiseaseExtractor, DiseaseDict
from .location_extractor import LocationExtractor, LocationDict
from .processor import EpiWatchNLPProcessor, TextProcessor, ConfidenceCalculator, NLPResult

__all__ = [
    "DiseaseExtractor",
    "LocationExtractor", 
    "TextProcessor",
    "ConfidenceCalculator",
    "DiseaseDict",
    "LocationDict",
    "EpiWatchNLPProcessor",
    "NLPResult"
]