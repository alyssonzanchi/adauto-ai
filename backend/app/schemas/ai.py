"""
AI Schemas - Pydantic schemas for AI agent predictions
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


# ==================== PREDICTION ====================

class PredictionRequest(BaseModel):
    """Request for performance prediction"""
    vehicle_id: str = Field(..., description="Vehicle ID")
    forecast_days: int = Field(30, ge=7, le=90, description="Forecast period (7, 30, or 90 days)")
    include_scenarios: bool = Field(False, description="Include budget scenarios")
    target_budget: Optional[float] = Field(None, description="Target budget for scenario analysis")


class ForecastDaily(BaseModel):
    """Daily forecast data"""
    day: int
    date: str
    impressions: int
    clicks: float
    conversions: float
    ctr: float
    conversion_rate: float


class ForecastTotals(BaseModel):
    """Forecast totals"""
    impressions: int
    clicks: float
    conversions: float
    avg_ctr: float
    avg_conversion_rate: float


class ForecastData(BaseModel):
    """Complete forecast data"""
    period_days: int
    daily_predictions: List[ForecastDaily]
    totals: ForecastTotals


class RiskAssessment(BaseModel):
    """Risk assessment"""
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0=low, 1=high)")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    risk_factors: List[str] = Field(default_factory=list, description="List of risk factors")


class PredictionResponse(BaseModel):
    """Response from prediction endpoint"""
    vehicle_id: str
    predictions: Dict[str, Any]
    forecast: ForecastData
    risk_assessment: RiskAssessment
    confidence: float = Field(..., ge=0, le=1)


# ==================== OPTIMIZATION ====================

class OptimizationGoals(BaseModel):
    """Optimization goals"""
    target_ctr: Optional[float] = Field(None, ge=0, le=1)
    target_conversion: Optional[float] = Field(None, ge=0, le=1)
    target_budget: Optional[float] = Field(None)


class ContentOptimization(BaseModel):
    """Content optimization recommendations"""
    recommendations: List[Dict[str, Any]]
    priority_order: List[str]


class BidRecommendations(BaseModel):
    """Bid recommendations"""
    recommended_bid: float
    min_bid: float
    max_bid: float
    reasoning: str
    bid_strategy: str


class BudgetOptimization(BaseModel):
    """Budget optimization recommendations"""
    recommendations: List[Dict[str, Any]]
    optimal_daily_budget: float


class ABTestSuggestion(BaseModel):
    """A/B test suggestion"""
    test_type: str
    test_name: str
    variants: List[str]
    success_metric: str
    expected_winner: Optional[str] = None
    duration_days: Optional[int] = None


class OptimizationResponse(BaseModel):
    """Response from optimization endpoint"""
    content_optimization: ContentOptimization
    bid_recommendations: BidRecommendations
    budget_optimization: BudgetOptimization
    suggested_tests: List[ABTestSuggestion]
    optimization_priority: List[str]


# ==================== EVALUATION ====================

class EvaluationRequest(BaseModel):
    """Request for content evaluation"""
    ad_content: Dict[str, Any]
    vehicle_id: Optional[str] = None
    include_benchmark: bool = True


class ContentAnalysis(BaseModel):
    """Content analysis scores"""
    headline_quality: float
    description_quality: float
    image_quality: float
    cta_quality: float
    word_count: int
    character_count: int


class BenchmarkComparison(BaseModel):
    """Benchmark comparison data"""
    vs_industry: Dict[str, float]
    vs_top_10: Dict[str, float]
    industry_average: float
    top_10_percent: float
    percentile: float


class EvaluationResponse(BaseModel):
    """Response from evaluation endpoint"""
    quality_score: int = Field(..., ge=0, le=100, description="Overall quality score 0-100")
    quality_grade: str = Field(..., description="Letter grade A+ to D")
    content_analysis: ContentAnalysis
    gaps: List[str]
    benchmark_comparison: Optional[BenchmarkComparison]
    recommendations: List[str]
