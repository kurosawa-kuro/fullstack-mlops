"""
FastAPI application for house price prediction.

This module provides REST API endpoints for predicting house prices
using a trained machine learning model.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from inference import batch_predict, predict_price
from schemas import HousePredictionRequest, PredictionResponse

# Initialize FastAPI app with metadata
app = FastAPI(
    title="House Price Prediction API",
    description=(
        "An API for predicting house prices based on various features. "
        "This application is part of the MLOps Bootcamp by School of Devops. "
        "Authored by Gourav Shah."
    ),
    version="1.0.0",
    contact={
        "name": "School of Devops",
        "url": "https://schoolofdevops.com",
        "email": "learn@schoolofdevops.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=dict)
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Status information about the API
    """
    return {"status": "healthy", "model_loaded": True}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: HousePredictionRequest):
    """
    Single prediction endpoint.

    Args:
        request: House prediction request data

    Returns:
        PredictionResponse: Predicted house price and confidence interval
    """
    return predict_price(request)


@app.post("/batch-predict", response_model=list)
async def batch_predict_endpoint(requests: list[HousePredictionRequest]):
    """
    Batch prediction endpoint.

    Args:
        requests: List of house prediction request data

    Returns:
        list: List of predicted house prices
    """
    return batch_predict(requests)
