"""
Base Model - Abstract base class for all ML models
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import joblib
import numpy as np
from pathlib import Path


class BaseModel(ABC):
    """
    Abstract base class for all ML models.

    Provides common functionality:
    - Model loading/saving
    - Prediction interface
    - Feature validation
    - Model metadata
    """

    def __init__(self, model_name: str):
        """
        Initialize base model.

        Args:
            model_name: Name of the model (e.g., "price_predictor")
        """
        self.model_name = model_name
        self.model = None
        self.feature_names: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.is_trained = False

    @abstractmethod
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction on features.

        Args:
            features: Dictionary of features

        Returns:
            Dictionary with prediction results
        """
        pass

    @abstractmethod
    async def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Make batch predictions.

        Args:
            features_list: List of feature dictionaries

        Returns:
            List of prediction results
        """
        pass

    def load_model(self, model_path: str) -> bool:
        """
        Load trained model from disk.

        Args:
            model_path: Path to model file

        Returns:
            True if successful, False otherwise
        """
        try:
            model_file = Path(model_path)
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")

            # Load model
            model_data = joblib.load(model_path)

            # Extract model and metadata
            self.model = model_data.get("model")
            self.feature_names = model_data.get("feature_names", [])
            self.metadata = model_data.get("metadata", {})
            self.is_trained = True

            return True

        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def save_model(self, model_path: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save trained model to disk.

        Args:
            model_path: Path to save model
            metadata: Optional metadata to save with model

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.model is None:
                raise ValueError("No model to save")

            # Prepare metadata
            save_metadata = {
                "model_name": self.model_name,
                "saved_at": datetime.now().isoformat(),
                "feature_names": self.feature_names,
                "is_trained": self.is_trained,
            }

            if metadata:
                save_metadata.update(metadata)

            if self.metadata:
                save_metadata.update(self.metadata)

            # Save model
            model_data = {
                "model": self.model,
                "feature_names": self.feature_names,
                "metadata": save_metadata
            }

            # Create directory if needed
            model_file = Path(model_path)
            model_file.parent.mkdir(parents=True, exist_ok=True)

            joblib.dump(model_data, model_path)

            return True

        except Exception as e:
            print(f"Error saving model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.

        Returns:
            Dictionary with model metadata
        """
        return {
            "model_name": self.model_name,
            "is_trained": self.is_trained,
            "feature_count": len(self.feature_names),
            "metadata": self.metadata
        }

    def validate_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input features.

        Args:
            features: Dictionary of features

        Returns:
            Validation result with status and issues
        """
        validation = {
            "is_valid": True,
            "missing_features": [],
            "extra_features": [],
            "invalid_values": []
        }

        # Check for missing features (if model is trained)
        if self.is_trained and self.feature_names:
            for feature_name in self.feature_names:
                if feature_name not in features:
                    validation["missing_features"].append(feature_name)
                    validation["is_valid"] = False

        # Check for invalid values (None, NaN, inf)
        for key, value in features.items():
            if value is None:
                validation["invalid_values"].append(f"{key}=None")
                validation["is_valid"] = False
            elif isinstance(value, float):
                if np.isnan(value) or np.isinf(value):
                    validation["invalid_values"].append(f"{key}={value}")
                    validation["is_valid"] = False

        return validation

    def _features_to_array(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Convert features dict to numpy array.

        Args:
            features: Dictionary of features

        Returns:
            numpy array with feature values
        """
        if self.is_trained and self.feature_names:
            # Use trained feature order
            values = []
            for name in self.feature_names:
                value = features.get(name, 0)  # Default to 0 if missing
                values.append(value)
            return np.array(values).reshape(1, -1)
        else:
            # Use all features in alphabetical order
            values = [features[key] for key in sorted(features.keys())]
            return np.array(values).reshape(1, -1)

    def set_feature_names(self, feature_names: List[str]) -> None:
        """
        Set feature names for the model.

        Args:
            feature_names: List of feature names
        """
        self.feature_names = feature_names

    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Update model metadata.

        Args:
            metadata: Dictionary of metadata to update
        """
        self.metadata.update(metadata)
