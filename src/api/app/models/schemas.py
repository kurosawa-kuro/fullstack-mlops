"""
Pydantic schemas for house price prediction API.

This module defines the data models for request and response validation.
"""

from typing import List

from pydantic import BaseModel, Field


class HousePredictionRequest(BaseModel):
    """
    Request model for house price prediction.

    Attributes:
        sqft: Square footage of the house
        bedrooms: Number of bedrooms
        bathrooms: Number of bathrooms
        location: Location of the house
        year_built: Year the house was built
        condition: Condition of the house
    """

    sqft: float = Field(..., gt=0, description="Square footage of the house")
    bedrooms: int = Field(..., ge=1, description="Number of bedrooms")
    bathrooms: float = Field(..., gt=0, description="Number of bathrooms")
    location: str = Field(..., description="Location (urban, suburban, rural)")
    year_built: int = Field(
        ..., ge=1800, le=2023, description="Year the house was built"
    )
    condition: str = Field(
        ..., description="Condition of the house (e.g., Good, Excellent, Fair)"
    )


class PredictionResponse(BaseModel):
    """
    Response model for house price prediction.

    Attributes:
        predicted_price: Predicted house price
        confidence_interval: Confidence interval for the prediction
        features_importance: Feature importance scores
        prediction_time: Timestamp of the prediction
    """

    predicted_price: float
    confidence_interval: List[float]
    features_importance: dict
    prediction_time: str 