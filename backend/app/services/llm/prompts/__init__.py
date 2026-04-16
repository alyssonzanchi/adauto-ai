"""
Prompt templates for AI agents.
"""
from app.services.llm.prompts.base import BasePromptTemplate
from app.services.llm.prompts.vehicle_analysis import VehicleAnalysisPrompt
from app.services.llm.prompts.ad_generation import AdGenerationPrompt
from app.services.llm.prompts.price_scoring import PriceScoringPrompt

__all__ = [
    "BasePromptTemplate",
    "VehicleAnalysisPrompt",
    "AdGenerationPrompt",
    "PriceScoringPrompt",
]
