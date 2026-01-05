"""
Meowzon OCR Extractor - AI-Hybrid Amazon Order Extraction
"""

__version__ = "3.0.0"
__author__ = "Meowzon Team"
__description__ = "Cat-themed AI-hybrid OCR tool for extracting Amazon order details"

from .config import ExtractorConfig
from .extractor import MeowzonExtractor
from .interactive_review import run_interactive_review

__all__ = [
    'ExtractorConfig',
    'MeowzonExtractor',
    'run_interactive_review',
]
