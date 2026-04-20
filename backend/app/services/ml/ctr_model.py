"""
CTR Model - XGBoost model for Click-Through Rate prediction
"""
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path

from .base_model import BaseModel
from app.ml.features import FeatureEngineer


class CTRModel(BaseModel):
    """
    XGBoost-based model for CTR prediction.

    Predicts:
    - predicted_ctr: Predicted CTR (0-1)
    - ctr_bucket: Category (very_low, low, medium, high, very_high)
    - optimization_suggestions: List of suggestions to improve CTR
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize CTRModel.

        Args:
            model_path: Optional path to trained model
        """
        super().__init__("ctr_predictor")

        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer(db_session=None)

        # Try to load model if path provided
        if model_path:
            self.load_model(model_path)

    async def predict(
        self,
        vehicle_data: Dict[str, Any],
        ad_content: Optional[Dict[str, Any]] = None,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict CTR for a vehicle ad.

        Args:
            vehicle_data: Vehicle information
            ad_content: Optional ad content (headline, description, images)
            interaction_data: Optional historical interaction data

        Returns:
            Dictionary with:
                - predicted_ctr: Predicted CTR (0-1)
                - ctr_bucket: Category (very_low, low, medium, high, very_high)
                - confidence: Confidence score 0-1
                - optimization_suggestions: List of suggestions
        """
        # Extract vehicle features
        features = await self.feature_engineer.extract_features(vehicle_data)

        # Add ad content features
        if ad_content:
            ad_features = self._extract_ad_features(ad_content)
            features.update(ad_features)

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
            return self._fallback_prediction(vehicle_data, features, ad_content)

        # Prepare features for model
        X = self._features_to_array(features)

        # Make prediction
        try:
            predicted_ctr = float(self.model.predict(X)[0])

            # Clamp to 0-1
            predicted_ctr = max(0.0, min(1.0, predicted_ctr))

            # Calculate bucket
            ctr_bucket = self._calculate_ctr_bucket(predicted_ctr)

            # Calculate confidence
            confidence = self._calculate_confidence(features)

            # Generate optimization suggestions
            suggestions = self._generate_suggestions(features, predicted_ctr)

            return {
                "predicted_ctr": round(predicted_ctr, 4),
                "ctr_bucket": ctr_bucket,
                "confidence": round(confidence, 3),
                "optimization_suggestions": suggestions
            }

        except Exception as e:
            print(f"Prediction error: {e}")
            return self._fallback_prediction(vehicle_data, features, ad_content)

    async def predict_batch(
        self,
        vehicles_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Make batch predictions"""
        results = []
        for vehicle_data in vehicles_data:
            result = await self.predict(vehicle_data)
            results.append(result)
        return results

    def _extract_ad_features(self, ad_content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from ad content"""
        features = {}

        # Headline
        headline = ad_content.get("headline", "")
        features["headline_length"] = len(headline)
        features["headline_word_count"] = len(headline.split())
        features["has_emoji"] = 1 if any(c in headline for c in "😀😃😄😁🚗🚙") else 0
        features["has_numbers"] = 1 if any(c.isdigit() for c in headline) else 0

        # Description
        description = ad_content.get("description", "")
        features["description_length"] = len(description)
        features["description_word_count"] = len(description.split())

        # Images
        images = ad_content.get("images", [])
        features["ad_image_count"] = len(images)
        features["has_main_image"] = 1 if len(images) > 0 else 0
        features["has_multiple_images"] = 1 if len(images) >= 3 else 0

        # Call to action
        cta = ad_content.get("cta", "")
        features["has_cta"] = 1 if len(cta) > 0 else 0
        features["cta_length"] = len(cta)

        # Content quality score
        features["content_quality_score"] = self._calculate_content_quality(features)

        return features

    def _calculate_content_quality(self, ad_features: Dict[str, Any]) -> float:
        """Calculate content quality score (0-1)"""
        score = 0.0

        # Headline quality (30-60 chars ideal)
        headline_len = ad_features.get("headline_length", 0)
        if 30 <= headline_len <= 60:
            score += 0.3
        elif headline_len > 0:
            score += 0.1

        # Image count (3-5 images ideal)
        img_count = ad_features.get("ad_image_count", 0)
        if 3 <= img_count <= 5:
            score += 0.3
        elif img_count >= 1:
            score += 0.15

        # Has CTA
        if ad_features.get("has_cta"):
            score += 0.2

        # Has engaging elements
        if ad_features.get("has_emoji") or ad_features.get("has_numbers"):
            score += 0.2

        return min(score, 1.0)

    def _calculate_ctr_bucket(self, ctr: float) -> str:
        """Calculate CTR bucket category"""
        if ctr < 0.01:
            return "very_low"
        elif ctr < 0.02:
            return "low"
        elif ctr < 0.04:
            return "medium"
        elif ctr < 0.06:
            return "high"
        else:
            return "very_high"

    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate prediction confidence"""
        confidence = 0.5  # Base confidence

        # Increase with quality signals
        if features.get("content_quality_score", 0) > 0.7:
            confidence += 0.15

        if features.get("demand_score", 0) > 0.5:
            confidence += 0.15

        if features.get("is_fresh_listing", 0) == 1:
            confidence += 0.1

        if features.get("image_count", 0) >= 3:
            confidence += 0.1

        return min(confidence, 1.0)

    def _generate_suggestions(
        self,
        features: Dict[str, Any],
        predicted_ctr: float
    ) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []

        # Low CTR suggestions
        if predicted_ctr < 0.02:
            suggestions.append("Melhore o título do anúncio (tente 30-60 caracteres)")
            suggestions.append("Adicione mais imagens (mínimo 3-5 fotos)")
            suggestions.append("Inclua preços e informações-chave no título")

        # Image suggestions
        if features.get("image_count", 0) < 3:
            suggestions.append("Adicione mais fotos do veículo (interior, exterior, detalhes)")

        # Content suggestions
        if features.get("content_quality_score", 0) < 0.5:
            suggestions.append("Melhore a qualidade do conteúdo do anúncio")
            suggestions.append("Adicione call-to-action claro")

        # Price suggestions
        price_position = features.get("price_position", "")
        if price_position == "overpriced":
            suggestions.append("Considere ajustar o preço para melhor posicionamento")

        # Timing suggestions
        if features.get("days_since_listing", 0) > 60:
            suggestions.append("Anúncio antigo - considere atualizar ou republicar")

        return suggestions

    def _fallback_prediction(
        self,
        vehicle_data: Dict[str, Any],
        features: Dict[str, Any],
        ad_content: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback prediction using heuristics"""
        # Base CTR
        base_ctr = 0.025  # 2.5% industry average

        # Adjust based on factors
        ctr = base_ctr

        # Demand adjustment
        demand_score = features.get("demand_score", 0.5)
        ctr *= (0.5 + demand_score)

        # Image adjustment
        image_count = features.get("image_count", 0)
        if image_count >= 5:
            ctr *= 1.3
        elif image_count >= 3:
            ctr *= 1.1
        elif image_count == 0:
            ctr *= 0.3

        # Price position adjustment
        price_position = features.get("price_position", "")
        if price_position == "great_deal":
            ctr *= 1.4
        elif price_position == "good_price":
            ctr *= 1.2
        elif price_position == "overpriced":
            ctr *= 0.7

        # Fresh listing adjustment
        if features.get("is_fresh_listing", 0) == 1:
            ctr *= 1.1

        # Content quality adjustment
        if ad_content:
            content_score = self._calculate_content_quality(self._extract_ad_features(ad_content))
            ctr *= (0.7 + content_score)

        # Clamp to 0-1
        predicted_ctr = max(0.005, min(0.15, ctr))

        return {
            "predicted_ctr": round(predicted_ctr, 4),
            "ctr_bucket": self._calculate_ctr_bucket(predicted_ctr),
            "confidence": 0.5,
            "optimization_suggestions": self._generate_suggestions(features, predicted_ctr),
            "fallback": True
        }

    def train(
        self,
        X: np.ndarray,
        y_ctr: np.ndarray,
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
                    X, y_ctr,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
            else:
                self.model.fit(X, y_ctr, verbose=False)

            self.is_trained = True

            # Calculate metrics
            train_preds = self.model.predict(X)
            train_mae = np.mean(np.abs(train_preds - y_ctr))
            train_rmse = np.sqrt(np.mean((train_preds - y_ctr) ** 2))
            train_r2 = 1 - (np.sum((y_ctr - train_preds) ** 2) / np.sum((y_ctr - np.mean(y_ctr)) ** 2))

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
