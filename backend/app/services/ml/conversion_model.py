"""
Conversion Model - XGBoost model for conversion rate prediction
"""
from typing import Dict, Any, List, Optional
import numpy as np

from .base_model import BaseModel
from app.ml.features import FeatureEngineer


class ConversionModel(BaseModel):
    """
    XGBoost-based model for conversion prediction.

    Predicts:
    - predicted_conversion_rate: Predicted conversion rate (0-1)
    - conversion_probability: Category (low, medium, high)
    - lead_quality_score: Lead quality score (0-100)
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ConversionModel.

        Args:
            model_path: Optional path to trained model
        """
        super().__init__("conversion_predictor")

        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer(db_session=None)

        # Try to load model if path provided
        if model_path:
            self.load_model(model_path)

    async def predict(
        self,
        vehicle_data: Dict[str, Any],
        lead_data: Optional[Dict[str, Any]] = None,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict conversion rate for a vehicle/lead.

        Args:
            vehicle_data: Vehicle information
            lead_data: Optional lead information
            interaction_data: Optional interaction data

        Returns:
            Dictionary with:
                - predicted_conversion_rate: Predicted conversion (0-1)
                - conversion_probability: Category (low, medium, high)
                - lead_quality_score: Lead quality (0-100)
                - confidence: Confidence score 0-1
        """
        # Extract vehicle features
        features = await self.feature_engineer.extract_features(vehicle_data)

        # Add lead features
        if lead_data:
            lead_features = self._extract_lead_features(lead_data)
            features.update(lead_features)

        # Add interaction features
        if interaction_data:
            from app.ml.features.interaction_features import InteractionFeatures
            interaction_extractor = InteractionFeatures()
            interaction_feats = interaction_extractor.extract(interaction_data)
            features.update(interaction_feats)

        # Validate features
        validation = self.validate_features(features)
        if not validation["is_valid"]:
            raise ValueError(f"Invalid features: {validation}")

        # If model not trained, use fallback
        if not self.is_trained or self.model is None:
            return self._fallback_prediction(vehicle_data, features, lead_data)

        # Prepare features for model
        X = self._features_to_array(features)

        # Make prediction
        try:
            predicted_conversion = float(self.model.predict(X)[0])

            # Clamp to 0-1
            predicted_conversion = max(0.0, min(1.0, predicted_conversion))

            # Calculate probability bucket
            conversion_prob = self._calculate_conversion_probability(predicted_conversion)

            # Calculate lead quality score
            lead_quality = self._calculate_lead_quality(features)

            # Calculate confidence
            confidence = self._calculate_confidence(features)

            return {
                "predicted_conversion_rate": round(predicted_conversion, 4),
                "conversion_probability": conversion_prob,
                "lead_quality_score": lead_quality,
                "confidence": round(confidence, 3)
            }

        except Exception as e:
            print(f"Prediction error: {e}")
            return self._fallback_prediction(vehicle_data, features, lead_data)

    async def predict_batch(self, vehicles_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make batch predictions"""
        results = []
        for vehicle_data in vehicles_data:
            result = await self.predict(vehicle_data)
            results.append(result)
        return results

    def _extract_lead_features(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from lead data"""
        features = {}

        # Lead source
        lead_source = lead_data.get("source", "unknown").lower()
        features["lead_source_organic"] = 1 if lead_source == "organic" else 0
        features["lead_source_paid"] = 1 if lead_source in ["paid", "ads"] else 0
        features["lead_source_social"] = 1 if lead_source in ["social", "facebook", "instagram"] else 0
        features["lead_source_direct"] = 1 if lead_source == "direct" else 0

        # Lead type
        lead_type = lead_data.get("type", "unknown").lower()
        features["lead_type_hot"] = 1 if lead_type == "hot" else 0
        features["lead_type_warm"] = 1 if lead_type == "warm" else 0
        features["lead_type_cold"] = 1 if lead_type == "cold" else 0

        # Lead timing
        features["lead_response_time"] = lead_data.get("response_time", 0)  # minutes
        features["is_quick_response"] = 1 if features["lead_response_time"] < 30 else 0

        # Lead engagement
        features["lead_engagement_score"] = lead_data.get("engagement_score", 0.5)

        # Contact info completeness
        features["has_phone"] = 1 if lead_data.get("phone") else 0
        features["has_email"] = 1 if lead_data.get("email") else 0
        features["has_name"] = 1 if lead_data.get("name") else 0
        features["contact_completeness"] = (
            features["has_phone"] + features["has_email"] + features["has_name"]
        ) / 3.0

        return features

    def _calculate_conversion_probability(self, conversion_rate: float) -> str:
        """Calculate conversion probability category"""
        if conversion_rate < 0.01:
            return "low"
        elif conversion_rate < 0.03:
            return "medium"
        else:
            return "high"

    def _calculate_lead_quality(self, features: Dict[str, Any]) -> int:
        """Calculate lead quality score (0-100)"""
        score = 0

        # Price position (30 points)
        price_position = features.get("price_position", "")
        if price_position == "great_deal":
            score += 30
        elif price_position == "good_price":
            score += 25
        elif price_position == "fair_price":
            score += 15

        # Vehicle condition (25 points)
        condition = features.get("condition_score", 0.5)
        score += int(condition * 25)

        # Lead type (20 points)
        if features.get("lead_type_hot", 0) == 1:
            score += 20
        elif features.get("lead_type_warm", 0) == 1:
            score += 12
        elif features.get("lead_type_cold", 0) == 1:
            score += 5

        # Response time (15 points)
        if features.get("is_quick_response", 0) == 1:
            score += 15

        # Contact completeness (10 points)
        completeness = features.get("contact_completeness", 0)
        score += int(completeness * 10)

        return min(score, 100)

    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate prediction confidence"""
        confidence = 0.5

        # Increase with quality signals
        if features.get("condition_score", 0) > 0.7:
            confidence += 0.15

        if features.get("contact_completeness", 0) >= 1.0:
            confidence += 0.15

        if features.get("lead_type_hot", 0) == 1 or features.get("lead_type_warm", 0) == 1:
            confidence += 0.1

        if features.get("is_quick_response", 0) == 1:
            confidence += 0.1

        return min(confidence, 1.0)

    def _fallback_prediction(
        self,
        vehicle_data: Dict[str, Any],
        features: Dict[str, Any],
        lead_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback prediction using heuristics"""
        # Base conversion rate (2.5% industry average)
        base_conversion = 0.025

        # Adjust based on vehicle condition
        condition = features.get("condition_score", 0.5)
        conversion = base_conversion * (0.5 + condition)

        # Adjust for price position
        price_position = features.get("price_position", "")
        if price_position == "great_deal":
            conversion *= 1.5
        elif price_position == "good_price":
            conversion *= 1.3
        elif price_position == "overpriced":
            conversion *= 0.6

        # Adjust for lead quality
        if lead_data:
            lead_type = lead_data.get("type", "").lower()
            if lead_type == "hot":
                conversion *= 1.8
            elif lead_type == "warm":
                conversion *= 1.3
            elif lead_type == "cold":
                conversion *= 0.7

        # Adjust for response time
        if features.get("is_quick_response", 0) == 1:
            conversion *= 1.2

        # Clamp to 0-1
        predicted_conversion = max(0.005, min(0.15, conversion))

        # Calculate lead quality
        lead_quality = self._calculate_lead_quality(features)

        return {
            "predicted_conversion_rate": round(predicted_conversion, 4),
            "conversion_probability": self._calculate_conversion_probability(predicted_conversion),
            "lead_quality_score": lead_quality,
            "confidence": 0.5,
            "fallback": True
        }

    def train(
        self,
        X: np.ndarray,
        y_conversion: np.ndarray,
        feature_names: List[str],
        validation_data: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Train the XGBoost model"""
        try:
            from xgboost import XGBRegressor

            # Set feature names
            self.set_feature_names(feature_names)

            # Create model
            self.model = XGBRegressor(
                n_estimators=150,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )

            # Train
            if validation_data:
                X_val, y_val = validation_data
                self.model.fit(
                    X, y_conversion,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
            else:
                self.model.fit(X, y_conversion, verbose=False)

            self.is_trained = True

            # Calculate metrics
            train_preds = self.model.predict(X)
            train_mae = np.mean(np.abs(train_preds - y_conversion))
            train_rmse = np.sqrt(np.mean((train_preds - y_conversion) ** 2))
            train_r2 = 1 - (np.sum((y_conversion - train_preds) ** 2) / np.sum((y_conversion - np.mean(y_conversion)) ** 2))

            metrics = {
                "train_mae": float(train_mae),
                "train_rmse": float(train_rmse),
                "train_r2": float(train_r2),
                "feature_importance": dict(zip(
                    feature_names,
                    self.model.feature_importances_.tolist()
                ))
            }

            # Add validation metrics if provided
            if validation_data:
                X_val, y_val = validation_data
                val_preds = self.model.predict(X_val)
                val_mae = np.mean(np.abs(val_preds - y_val))
                val_rmse = np.sqrt(np.mean((val_preds - y_val) ** 2))
                val_r2 = 1 - (np.sum((y_val - val_preds) ** 2) / np.sum((y_val - np.mean(y_val)) ** 2))

                metrics.update({
                    "val_mae": float(val_mae),
                    "val_rmse": float(val_rmse),
                    "val_r2": float(val_r2)
                })

            return metrics

        except Exception as e:
            print(f"Training error: {e}")
            raise
