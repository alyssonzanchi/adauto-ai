"""
Price Model - XGBoost model for price prediction and scoring
"""
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path

from .base_model import BaseModel
from app.ml.features import FeatureEngineer


class PriceModel(BaseModel):
    """
    XGBoost-based model for vehicle price prediction.

    Predicts:
    - fair_market_price: Regression target
    - price_score: Classification score (0-100)
    - price_position: Category (great_deal, good_price, fair_price, overpriced)
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize PriceModel.

        Args:
            model_path: Optional path to trained model
        """
        super().__init__("price_predictor")

        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer(db_session=None)

        # Try to load model if path provided
        if model_path:
            self.load_model(model_path)

    async def predict(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict price and scoring for a vehicle.

        Args:
            vehicle_data: Dictionary with vehicle information

        Returns:
            Dictionary with:
                - predicted_price: Predicted fair market price
                - price_range: [min, max] price range
                - price_score: Score 0-100 (higher = better deal)
                - price_position: Category (great_deal, good_price, etc.)
                - confidence: Confidence score 0-1
        """
        # Extract features
        features = await self.feature_engineer.extract_features(vehicle_data)

        # Validate features
        validation = self.validate_features(features)
        if not validation["is_valid"]:
            raise ValueError(f"Invalid features: {validation}")

        # If model not trained, use fallback (simple estimation)
        if not self.is_trained or self.model is None:
            return self._fallback_prediction(vehicle_data, features)

        # Prepare features for model
        X = self._features_to_array(features)

        # Make prediction
        try:
            # Predict price
            predicted_price = float(self.model.predict(X)[0])

            # Calculate price score and position
            current_price = vehicle_data.get("price", 0)
            price_score, price_position = self._calculate_price_score(
                current_price,
                predicted_price
            )

            # Calculate confidence (based on feature quality)
            confidence = self._calculate_confidence(features)

            # Calculate price range (±10%)
            price_range = [
                predicted_price * 0.9,
                predicted_price * 1.1
            ]

            return {
                "predicted_price": round(predicted_price, 2),
                "price_range": [round(p, 2) for p in price_range],
                "price_score": price_score,
                "price_position": price_position,
                "confidence": round(confidence, 3)
            }

        except Exception as e:
            print(f"Prediction error: {e}")
            return self._fallback_prediction(vehicle_data, features)

    async def predict_batch(self, vehicles_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Make batch predictions.

        Args:
            vehicles_data: List of vehicle dictionaries

        Returns:
            List of prediction results
        """
        results = []
        for vehicle_data in vehicles_data:
            result = await self.predict(vehicle_data)
            results.append(result)
        return results

    def _calculate_price_score(
        self,
        current_price: float,
        predicted_price: float
    ) -> tuple[int, str]:
        """
        Calculate price score and position.

        Args:
            current_price: Current listed price
            predicted_price: Predicted fair price

        Returns:
            Tuple of (score: int, position: str)
        """
        if predicted_price == 0:
            return 50, "fair_price"

        # Calculate price difference percentage
        diff_pct = (predicted_price - current_price) / predicted_price

        # Calculate score (0-100)
        # Score > 50 means underpriced (good deal)
        # Score < 50 means overpriced
        # Score = 50 means fair priced
        score = int(50 + (diff_pct * 200))  # Scale difference
        score = max(0, min(100, score))  # Clamp to 0-100

        # Determine position category
        if diff_pct > 0.15:  # > 15% below predicted
            position = "great_deal"
        elif diff_pct > 0.05:  # 5-15% below predicted
            position = "good_price"
        elif diff_pct > -0.05:  # ±5% of predicted
            position = "fair_price"
        elif diff_pct > -0.15:  # 5-15% above predicted
            position = "expensive"
        else:  # > 15% above predicted
            position = "overpriced"

        return score, position

    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """
        Calculate prediction confidence based on feature quality.

        Args:
            features: Dictionary of features

        Returns:
            Confidence score 0-1
        """
        confidence = 0.5  # Base confidence

        # Increase confidence if we have good features
        if features.get("age_years", 0) < 10:
            confidence += 0.1

        if features.get("mileage", 0) < 100000:
            confidence += 0.1

        if features.get("condition_score", 0) > 0.5:
            confidence += 0.1

        if features.get("demand_score", 0) > 0:
            confidence += 0.1

        if features.get("supply_score", 0) > 0:
            confidence += 0.1

        return min(confidence, 1.0)

    def _fallback_prediction(
        self,
        vehicle_data: Dict[str, Any],
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback prediction when model is not trained.

        Uses simple heuristics based on depreciation.

        Args:
            vehicle_data: Vehicle data
            features: Extracted features

        Returns:
            Prediction dictionary
        """
        # Get base price from vehicle
        current_price = vehicle_data.get("price", 0)

        # Apply depreciation
        age_years = features.get("age_years", 0)
        mileage = features.get("mileage", 0)

        # Simple depreciation: 15% per year, max 70%
        depreciation = min(0.15 * age_years + (mileage / 100000) * 0.1, 0.7)

        # Estimated new price (reverse depreciation)
        if current_price > 0:
            estimated_new_price = current_price / (1 - depreciation) if depreciation < 1 else current_price * 1.3
            predicted_price = current_price * (1 - depreciation * 0.5)  # Midpoint
        else:
            predicted_price = 100000  # Default

        # Calculate score and position
        price_score, price_position = self._calculate_price_score(
            current_price,
            predicted_price
        )

        # Price range (wider for fallback)
        price_range = [
            predicted_price * 0.8,
            predicted_price * 1.2
        ]

        return {
            "predicted_price": round(predicted_price, 2),
            "price_range": [round(p, 2) for p in price_range],
            "price_score": price_score,
            "price_position": price_position,
            "confidence": 0.5,  # Lower confidence for fallback
            "fallback": True  # Indicate this is a fallback prediction
        }

    def train(
        self,
        X: np.ndarray,
        y_price: np.ndarray,
        feature_names: List[str],
        validation_data: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Train the XGBoost model.

        Args:
            X: Feature matrix
            y_price: Target prices
            feature_names: List of feature names
            validation_data: Optional tuple (X_val, y_val)

        Returns:
            Training metrics
        """
        try:
            from xgboost import XGBRegressor

            # Set feature names
            self.set_feature_names(feature_names)

            # Create model
            self.model = XGBRegressor(
                n_estimators=200,
                max_depth=5,
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
                    X,
                    y_price,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
            else:
                self.model.fit(
                    X,
                    y_price,
                    verbose=False
                )

            self.is_trained = True

            # Calculate metrics
            train_preds = self.model.predict(X)
            train_mae = np.mean(np.abs(train_preds - y_price))
            train_rmse = np.sqrt(np.mean((train_preds - y_price) ** 2))
            train_r2 = 1 - (np.sum((y_price - train_preds) ** 2) / np.sum((y_price - np.mean(y_price)) ** 2))

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
