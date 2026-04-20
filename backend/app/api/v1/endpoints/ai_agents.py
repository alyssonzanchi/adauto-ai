"""
AI Agents API Endpoints - Predictor, Optimizer and Evaluator agents
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.ai import (
    PredictionRequest,
    PredictionResponse,
    OptimizationRequest,
    OptimizationResponse,
    EvaluationRequest,
    EvaluationResponse
)


router = APIRouter()


# Initialize agents (lazy loading)
_predictor_agent = None
_optimizer_agent = None
_evaluator_agent = None


def get_predictor_agent():
    """Get or initialize PredictorAgent"""
    global _predictor_agent
    if _predictor_agent is None:
        from app.services.ai.agents.predictor import PredictorAgent
        from app.services.llm.llm_client import LLMClient

        llm_client = LLMClient()
        _predictor_agent = PredictorAgent(llm_client)
    return _predictor_agent


def get_optimizer_agent():
    """Get or initialize OptimizerAgent"""
    global _optimizer_agent
    if _optimizer_agent is None:
        from app.services.ai.agents.optimizer import OptimizerAgent
        from app.services.llm.llm_client import LLMClient

        llm_client = LLMClient()
        _optimizer_agent = OptimizerAgent(llm_client)
    return _optimizer_agent


def get_evaluator_agent():
    """Get or initialize EvaluatorAgent"""
    global _evaluator_agent
    if _evaluator_agent is None:
        from app.services.ai.agents.evaluator import EvaluatorAgent
        from app.services.llm.llm_client import LLMClient

        llm_client = LLMClient()
        _evaluator_agent = EvaluatorAgent(llm_client)
    return _evaluator_agent


@router.get("/predict/{vehicle_id}", response_model=PredictionResponse)
async def predict_performance(
    vehicle_id: str,
    forecast_days: int = 30,
    include_scenarios: bool = False,
    target_budget: float = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Predict ad performance for a vehicle.

    Args:
        vehicle_id: Vehicle ID
        forecast_days: Forecast period (7, 30, or 90)
        include_scenarios: Include budget scenario analysis
        target_budget: Target budget for scenarios

    Returns:
        Complete prediction with forecast and risk assessment
    """
    try:
        # Get vehicle data
        from sqlalchemy import select
        from app.models.vehicle import Vehicle

        result = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )

        # Convert to dict
        vehicle_data = {
            "id": str(vehicle.id),
            "brand": vehicle.brand,
            "model": vehicle.model,
            "model_year": vehicle.model_year,
            "year": vehicle.year,
            "mileage": float(vehicle.mileage) if vehicle.mileage else 0,
            "color": vehicle.color or "",
            "transmission": vehicle.transmission or "",
            "fuel_type": vehicle.fuel_type or "",
            "body_type": vehicle.body_type or "",
            "doors": vehicle.doors or 4,
            "engine_capacity": float(vehicle.engine_capacity) if vehicle.engine_capacity else 2.0,
            "horsepower": float(vehicle.horsepower) if vehicle.horsepower else 150,
            "price": float(vehicle.price) if vehicle.price else 0,
            "status": vehicle.status or "available",
            "created_at": vehicle.created_at,
            "days_since_listing": (vehicle.created_at - datetime.now()).days if vehicle.created_at else 0
        }

        # Get agent and predict
        agent = get_predictor_agent()
        prediction = await agent._execute_with_metrics({
            "vehicle_data": vehicle_data,
            "forecast_days": forecast_days,
            "target_budget": target_budget,
            "include_scenarios": include_scenarios
        })

        return PredictionResponse(**prediction)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@router.post("/optimize")
async def optimize_ad(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Optimize ad content and strategy.

    Args:
        request: Optimization request with vehicle_data, ad_content, goals

    Returns:
        Optimization recommendations including content, bids, budget, and A/B tests
    """
    try:
        agent = get_optimizer_agent()
        optimization = await agent._execute_with_metrics({
            "vehicle_data": request.vehicle_data,
            "ad_content": request.ad_content,
            "current_metrics": request.current_metrics or {},
            "goals": request.goals or {}
        })

        return OptimizationResponse(**optimization)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization error: {str(e)}"
        )


@router.post("/evaluate")
async def evaluate_content(
    request: EvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluate ad content quality.

    Args:
        request: Evaluation request with ad_content and vehicle_id

    Returns:
        Quality score, content analysis, benchmarking, and recommendations
    """
    try:
        agent = get_evaluator_agent()
        evaluation = await agent._execute_with_metrics({
            "ad_content": request.ad_content,
            "vehicle_id": request.vehicle_id,
            "include_benchmark": request.include_benchmark
        })

        return EvaluationResponse(**evaluation)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation error: {str(e)}"
        )


@router.get("/agents/info")
async def get_agents_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about available AI agents.

    Returns:
        List of agents with status and capabilities
    """
    from app.services.ai.agents.predictor import PredictorAgent
    from app.services.ai.agents.optimizer import OptimizerAgent
    from app.services.ai.agents.evaluator import EvaluatorAgent

    return {
        "agents": [
            {
                "name": "PredictorAgent",
                "description": "Predict ad performance, forecasting, and risk assessment",
                "capabilities": [
                    "Performance prediction (CTR, conversion, ROI)",
                    "Forecasting (7d, 30d, 90d)",
                    "Scenario analysis",
                    "Risk assessment"
                ],
                "endpoint": "/api/v1/ai/predict/{vehicle_id}"
            },
            {
                "name": "OptimizerAgent",
                "description": "Optimize ad content and bidding strategy",
                "capabilities": [
                    "Content optimization (headline, description, CTA)",
                    "Bid recommendations",
                    "Budget optimization",
                    "A/B testing suggestions",
                    "Performance tips"
                ],
                "endpoint": "/api/v1/ai/optimize"
            },
            {
                "name": "EvaluatorAgent",
                "description": "Evaluate content quality and benchmarking",
                "capabilities": [
                    "Quality scoring (0-100)",
                    "Content analysis",
                    "Benchmarking vs industry",
                    "Gap analysis",
                    "Improvement roadmap"
                ],
                "endpoint": "/api/v1/ai/evaluate"
            }
        ]
    }
