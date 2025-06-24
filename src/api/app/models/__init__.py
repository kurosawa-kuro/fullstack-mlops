"""
Data models package for house price prediction API.

This package contains Pydantic schemas for request and response validation.
"""

from .schemas import HousePredictionRequest, PredictionResponse

__all__ = ["HousePredictionRequest", "PredictionResponse"] 