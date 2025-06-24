"""
Services package for house price prediction API.

This package contains business logic and inference services.
"""

from .inference import batch_predict, predict_price

__all__ = ["predict_price", "batch_predict"]
