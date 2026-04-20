"""
Feature Engineering - Orchestrates feature extraction for ML models
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import numpy as np

from .vehicle_features import VehicleFeatures
from .market_features import MarketFeatures
from .temporal_features import TemporalFeatures


class FeatureEngineer:
    """
    Orchestrates feature extraction from multiple sources.

    Combines:
    - Vehicle features (50+)
    - Market features (26+)
    - Temporal features (27+)

    Total: 100+ features
    """

    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize FeatureEngineer.

        Args:
            db_session: Optional database session for dynamic features
        """
        self.db_session = db_session
        self.vehicle_features = VehicleFeatures()
        self.market_features = MarketFeatures(db_session)
        self.temporal_features = TemporalFeatures()

    async def extract_features(
        self,
        vehicle_data: Dict[str, Any],
        reference_date: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Extract all features from vehicle data.

        Args:
            vehicle_data: Dictionary with vehicle information
            reference_date: Optional reference date for temporal features

        Returns:
            Dictionary with 100+ extracted features
        """
        # Extract vehicle features (synchronous)
        vehicle_feats = self.vehicle_features.extract(vehicle_data)

        # Extract market features (async - needs DB)
        market_feats = await self.market_features.extract(vehicle_data)

        # Extract temporal features (synchronous)
        if reference_date is None:
            temporal_feats = self.temporal_features.extract(vehicle_data)
        else:
            temporal_feats = self.temporal_features.extract(vehicle_data, reference_date)

        # Combine all features
        all_features = {}
        all_features.update(vehicle_feats)
        all_features.update(market_feats)
        all_features.update(temporal_feats)

        return all_features

    async def extract_features_batch(
        self,
        vehicles_data: List[Dict[str, Any]],
        reference_date: Optional[Any] = None
    ) -> pd.DataFrame:
        """
        Extract features for multiple vehicles.

        Args:
            vehicles_data: List of vehicle dictionaries
            reference_date: Optional reference date for temporal features

        Returns:
            DataFrame with features (rows=vehicles, cols=features)
        """
        features_list = []

        for vehicle_data in vehicles_data:
            features = await self.extract_features(vehicle_data, reference_date)
            features_list.append(features)

        return pd.DataFrame(features_list)

    def get_feature_names(self) -> List[str]:
        """
        Get list of all feature names.

        Returns:
            List of feature names (100+)
        """
        all_names = []
        all_names.extend(self.vehicle_features.get_feature_names())
        all_names.extend(self.market_features.get_feature_names())
        all_names.extend(self.temporal_features.get_feature_names())
        return all_names

    def get_feature_groups(self) -> Dict[str, List[str]]:
        """
        Get feature names grouped by category.

        Returns:
            Dictionary mapping category names to feature lists
        """
        groups = {}

        # Vehicle feature groups
        groups.update(self.vehicle_features.get_feature_importance_groups())

        # Market feature groups
        groups.update(self.market_features.get_feature_importance_groups())

        # Temporal feature groups
        groups.update(self.temporal_features.get_feature_importance_groups())

        return groups

    def get_feature_counts(self) -> Dict[str, int]:
        """
        Get count of features per category.

        Returns:
            Dictionary with feature counts
        """
        groups = self.get_feature_groups()
        return {category: len(features) for category, features in groups.items()}

    def validate_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted features.

        Args:
            features: Dictionary of extracted features

        Returns:
            Dictionary with validation results
        """
        validation = {
            "is_valid": True,
            "missing_features": [],
            "invalid_values": [],
            "warnings": []
        }

        # Check for None/NaN values
        for name, value in features.items():
            if value is None or (isinstance(value, float) and np.isnan(value)):
                validation["invalid_values"].append(name)
                validation["is_valid"] = False

        # Check for expected features (basic set)
        expected_basic = [
            "brand_honda", "model_year", "mileage",
            "price", "age_months", "condition_score"
        ]
        for expected in expected_basic:
            if expected not in features:
                validation["missing_features"].append(expected)
                validation["warnings"].append(f"Missing expected feature: {expected}")

        # Check for reasonable value ranges
        if "price" in features:
            price = features["price"]
            if price < 0:
                validation["invalid_values"].append("price (negative)")
                validation["is_valid"] = False
            elif price > 10000000:  # > R$ 10M
                validation["warnings"].append("price (suspiciously high)")

        if "mileage" in features:
            mileage = features["mileage"]
            if mileage < 0:
                validation["invalid_values"].append("mileage (negative)")
                validation["is_valid"] = False
            elif mileage > 500000:  # > 500k km
                validation["warnings"].append("mileage (suspiciously high)")

        return validation

    def prepare_for_model(
        self,
        features: Dict[str, Any],
        feature_names: Optional[List[str]] = None
    ) -> np.ndarray:
        """
        Convert features dict to numpy array for ML models.

        Args:
            features: Dictionary of extracted features
            feature_names: Optional list of feature names (order matters)

        Returns:
            numpy array with feature values
        """
        if feature_names is None:
            feature_names = self.get_feature_names()

        # Extract values in the correct order
        values = []
        for name in feature_names:
            value = features.get(name, 0)  # Default to 0 if missing
            values.append(value)

        return np.array(values)

    def get_feature_importance_mapping(self) -> Dict[str, str]:
        """
        Get mapping from feature names to human-readable descriptions.

        Returns:
            Dictionary mapping feature names to descriptions
        """
        return {
            # Brand
            "brand_honda": "Marca é Honda",
            "brand_toyota": "Marca é Toyota",
            "brand_volkswagen": "Marca é Volkswagen",
            "brand_chevrolet": "Marca é Chevrolet",
            "brand_ford": "Marca é Ford",
            "brand_other": "Outra marca",

            # Vehicle specs
            "model_year": "Ano do modelo",
            "year": "Ano de fabricação",
            "mileage": "Quilometragem",
            "age_months": "Idade em meses",
            "age_years": "Idade em anos",

            # Price
            "price": "Preço do veículo",
            "price_per_km": "Preço por km rodado",
            "depreciation_rate": "Taxa de depreciação",

            # Scores
            "condition_score": "Score de condição (0-1)",
            "feature_score": "Score de equipamentos (0-1)",
            "comfort_score": "Score de conforto (0-1)",
            "safety_score": "Score de segurança (0-1)",
            "technology_score": "Score de tecnologia (0-1)",

            # Market
            "demand_score": "Score de demanda (0-1)",
            "supply_score": "Score de oferta (0-1)",
            "competitor_count": "Número de concorrentes",
            "market_saturation": "Saturação de mercado (0-1)",

            # Temporal
            "days_since_listing": "Dias desde anúncio",
            "is_fresh_listing": "Anúncio recente (< 7 dias)",
            "is_weekend": "É fim de semana",
            "is_payday_period": "Período de pagamento",

            # Add more mappings as needed
        }

    def summarize_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a human-readable summary of key features.

        Args:
            features: Dictionary of extracted features

        Returns:
            Dictionary with summary information
        """
        summary = {}

        # Vehicle summary
        summary["vehicle"] = {
            "age_years": features.get("age_years", 0),
            "mileage": features.get("mileage", 0),
            "price": features.get("price", 0),
            "condition": features.get("condition_score", 0)
        }

        # Market summary
        summary["market"] = {
            "demand": features.get("demand_score", 0),
            "supply": features.get("supply_score", 0),
            "competition": features.get("competitor_count", 0),
            "saturation": features.get("market_saturation", 0)
        }

        # Temporal summary
        summary["timing"] = {
            "days_listed": features.get("days_since_listing", 0),
            "is_weekend": bool(features.get("is_weekend", 0)),
            "is_payday": bool(features.get("is_payday_period", 0)),
            "season": self._get_season_name(features)
        }

        # Overall scores
        summary["scores"] = {
            "feature_richness": features.get("feature_score", 0),
            "safety": features.get("safety_score", 0),
            "technology": features.get("technology_score", 0)
        }

        return summary

    def _get_season_name(self, features: Dict[str, Any]) -> str:
        """Get season name from features"""
        if features.get("is_summer"):
            return "Verão"
        elif features.get("is_winter"):
            return "Inverno"
        elif features.get("is_spring"):
            return "Primavera"
        elif features.get("is_fall"):
            return "Outono"
        else:
            return "N/A"
