"""
ML API Endpoints - Machine Learning prediction endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.ml import (
    PricePredictionRequest,
    PricePredictionResponse,
    CTRPredictionRequest,
    CTRPredictionResponse,
    ConversionPredictionRequest,
    ConversionPredictionResponse
)
from app.services.ml import PriceModel, CTRModel, ConversionModel


router = APIRouter()


# Initialize models (singleton)
price_model = PriceModel()
ctr_model = CTRModel()
conversion_model = ConversionModel()


@router.post("/predict-price", response_model=PricePredictionResponse)
async def predict_price(
    request: PricePredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict fair market price for a vehicle.

    Returns:
        - predicted_price: Predicted fair market price
        - price_range: Estimated price range [min, max]
        - price_score: Competitiveness score (0-100)
        - price_position: Category (great_deal, good_price, fair_price, expensive, overpriced)
        - confidence: Prediction confidence (0-1)
    """
    try:
        vehicle_data = request.vehicle_data.dict()

        # Make prediction
        prediction = await price_model.predict(vehicle_data)

        return PricePredictionResponse(**prediction)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@router.post("/predict-ctr", response_model=CTRPredictionResponse)
async def predict_ctr(
    request: CTRPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict Click-Through Rate for a vehicle ad.

    Args:
        - vehicle_data: Vehicle information
        - ad_content: Optional ad content (headline, description, images)
        - interaction_data: Optional historical interaction data

    Returns:
        - predicted_ctr: Predicted CTR (0-1)
        - ctr_bucket: Category (very_low, low, medium, high, very_high)
        - confidence: Prediction confidence (0-1)
        - optimization_suggestions: List of suggestions to improve CTR
    """
    try:
        vehicle_data = request.vehicle_data.dict()
        ad_content = request.ad_content.dict() if request.ad_content else None
        interaction_data = request.interaction_data.dict() if request.interaction_data else None

        # Make prediction
        prediction = await ctr_model.predict(
            vehicle_data,
            ad_content=ad_content,
            interaction_data=interaction_data
        )

        return CTRPredictionResponse(**prediction)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@router.post("/predict-conversion", response_model=ConversionPredictionResponse)
async def predict_conversion(
    request: ConversionPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict conversion rate for a vehicle/lead.

    Args:
        - vehicle_data: Vehicle information
        - lead_data: Optional lead information
        - interaction_data: Optional interaction data

    Returns:
        - predicted_conversion_rate: Predicted conversion (0-1)
        - conversion_probability: Category (low, medium, high)
        - lead_quality_score: Lead quality score (0-100)
        - confidence: Prediction confidence (0-1)
    """
    try:
        vehicle_data = request.vehicle_data.dict()
        lead_data = request.lead_data.dict() if request.lead_data else None
        interaction_data = request.interaction_data.dict() if request.interaction_data else None

        # Make prediction
        prediction = await conversion_model.predict(
            vehicle_data,
            lead_data=lead_data,
            interaction_data=interaction_data
        )

        return ConversionPredictionResponse(**prediction)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@router.get("/models/info")
async def get_models_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about available ML models.

    Returns:
        - List of models with status and metadata
    """
    return {
        "models": [
            {
                "name": "price_predictor",
                "version": "1.0.0",
                "status": "active",
                "description": "Predicts fair market price and competitiveness score",
                "endpoint": "/api/v1/ml/predict-price"
            },
            {
                "name": "ctr_predictor",
                "version": "1.0.0",
                "status": "active",
                "description": "Predicts click-through rate for ads",
                "endpoint": "/api/v1/ml/predict-ctr"
            },
            {
                "name": "conversion_predictor",
                "version": "1.0.0",
                "status": "active",
                "description": "Predicts conversion rate and lead quality",
                "endpoint": "/api/v1/ml/predict-conversion"
            }
        ]
    }
