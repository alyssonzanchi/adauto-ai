"""
Model Trainer - Train ML models
"""
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

from app.ml.features import FeatureEngineer
from app.services.ml.price_model import PriceModel
from app.services.ml.model_registry import ModelRegistry


class ModelTrainer:
    """
    Train ML models for vehicle predictions.

    Handles:
    - Feature extraction
    - Model training
    - Model evaluation
    - Model saving
    """

    def __init__(self, model_registry_path: str = "backend/app/ml/models"):
        """
        Initialize ModelTrainer.

        Args:
            model_registry_path: Path to model registry
        """
        self.feature_engineer = FeatureEngineer(db_session=None)
        self.model_registry = ModelRegistry(model_registry_path)

    async def train_price_model(
        self,
        vehicles_df: pd.DataFrame,
        model_version: str = "1.0.0",
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Train price prediction model.

        Args:
            vehicles_df: DataFrame with vehicle data
            model_version: Model version string
            test_size: Test set fraction
            random_state: Random seed

        Returns:
            Training metrics
        """
        print(f"Training price model with {len(vehicles_df)} samples...")

        # Extract features for all vehicles
        print("Extracting features...")
        features_list = []
        prices = []

        for _, row in vehicles_df.iterrows():
            vehicle_data = row.to_dict()
            features = await self.feature_engineer.extract_features(vehicle_data)
            features_list.append(features)
            prices.append(vehicle_data.get('price', 0))

        # Convert to arrays
        print("Preparing training data...")
        feature_names = self.feature_engineer.get_feature_names()

        # Create feature matrix
        X = []
        for features in features_list:
            row = []
            for fname in feature_names:
                row.append(features.get(fname, 0))
            X.append(row)

        X = np.array(X)
        y = np.array(prices)

        # Train/test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")

        # Train model
        print("Training XGBoost model...")
        model = PriceModel()
        metrics = model.train(
            X_train, y_train,
            feature_names=feature_names,
            validation_data=(X_test, y_test)
        )

        print("Training complete!")
        print(f"Train R²: {metrics['train_r2']:.4f}")
        print(f"Test R²: {metrics['val_r2']:.4f}")
        print(f"Test MAE: R$ {metrics['val_mae']:.2f}")

        # Save model
        print("Saving model...")
        model_path = f"backend/app/ml/models/price_predictor_{model_version}.pkl"

        save_metadata = {
            "version": model_version,
            "training_samples": len(vehicles_df),
            "test_samples": len(X_test),
            "train_r2": metrics["train_r2"],
            "val_r2": metrics["val_r2"],
            "val_mae": metrics["val_mae"],
            "val_rmse": metrics["val_rmse"],
            "feature_count": len(feature_names)
        }

        model.save_model(model_path, metadata=save_metadata)

        # Register model
        self.model_registry.register_model(
            "price_predictor",
            model_version,
            model.model,
            save_metadata
        )

        print(f"Model saved to: {model_path}")

        return metrics

    async def train_price_model_synthetic(
        self,
        n_samples: int = 1000,
        model_version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """
        Train price model on synthetic data.

        Args:
            n_samples: Number of synthetic samples
            model_version: Model version

        Returns:
            Training metrics
        """
        print(f"Generating {n_samples} synthetic samples...")

        # Generate synthetic data
        from app.ml.training.data_loader import DataLoader
        loader = DataLoader()
        vehicles_df = loader.generate_synthetic_data(n_samples=n_samples)

        return await self.train_price_model(vehicles_df, model_version)
