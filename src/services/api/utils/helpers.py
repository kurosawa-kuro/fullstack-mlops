"""
Helper utilities for house price prediction API.

This module contains utility functions for data validation, formatting,
and other common operations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_input_data(data: Dict[str, Any]) -> bool:
    """
    Validate input data for house price prediction.

    Args:
        data: Input data dictionary

    Returns:
        bool: True if data is valid, False otherwise
    """
    required_fields = [
        "sqft",
        "bedrooms",
        "bathrooms",
        "location",
        "year_built",
        "condition",
    ]

    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return False

    # Validate numeric fields
    if data["sqft"] <= 0:
        logger.error("Square footage must be positive")
        return False

    if data["bedrooms"] < 1:
        logger.error("Number of bedrooms must be at least 1")
        return False

    if data["bathrooms"] <= 0:
        logger.error("Number of bathrooms must be positive")
        return False

    if not (1800 <= data["year_built"] <= datetime.now().year):
        logger.error("Year built must be between 1800 and current year")
        return False

    return True


def format_prediction_response(
    price: float, confidence_interval: List[float]
) -> Dict[str, Any]:
    """
    Format prediction response with proper formatting.

    Args:
        price: Predicted price
        confidence_interval: Confidence interval

    Returns:
        Dict: Formatted response
    """
    return {
        "predicted_price": round(float(price), 2),
        "confidence_interval": [
            round(float(value), 2) for value in confidence_interval
        ],
        "prediction_time": datetime.now().isoformat(),
        "currency": "USD",
    }


def calculate_house_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate derived features for house price prediction.

    Args:
        data: Input DataFrame

    Returns:
        pd.DataFrame: DataFrame with calculated features
    """
    data = data.copy()

    # Calculate house age
    data["house_age"] = datetime.now().year - data["year_built"]

    # Calculate bedroom to bathroom ratio
    data["bed_bath_ratio"] = data["bedrooms"] / data["bathrooms"]

    # Add dummy price_per_sqft for compatibility
    data["price_per_sqft"] = 0

    return data


def log_prediction_request(request_data: Dict[str, Any], prediction: float) -> None:
    """
    Log prediction request and result for monitoring.

    Args:
        request_data: Input request data
        prediction: Predicted price
    """
    logger.info(
        f"Prediction request - Features: {request_data}, "
        f"Predicted Price: ${prediction:,.2f}"
    )
