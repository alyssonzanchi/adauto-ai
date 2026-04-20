"""
Train Price Model - Script to train XGBoost price prediction model
"""
import asyncio
import argparse
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.ml.training.trainer import ModelTrainer
from app.ml.training.data_loader import DataLoader


async def main():
    parser = argparse.ArgumentParser(description="Train price prediction model")
    parser.add_argument("--samples", type=int, default=1000, help="Number of training samples")
    parser.add_argument("--version", type=str, default="1.0.0", help="Model version")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set fraction")
    parser.add_argument("--synthetic", action="store_true", help="Use synthetic data")

    args = parser.parse_args()

    print("=" * 80)
    print("Training Price Prediction Model")
    print("=" * 80)
    print()

    # Initialize trainer
    trainer = ModelTrainer()

    if args.synthetic:
        # Train on synthetic data
        print(f"Generating {args.samples} synthetic training samples...")
        metrics = await trainer.train_price_model_synthetic(
            n_samples=args.samples,
            model_version=args.version
        )
    else:
        # Load data from database
        print("Loading data from database...")
        loader = DataLoader()
        vehicles_df = await loader.load_from_db(limit=args.samples)

        print(f"Loaded {len(vehicles_df)} vehicles from database")
        print()

        # Train model
        metrics = await trainer.train_price_model(
            vehicles_df=vehicles_df,
            model_version=args.version,
            test_size=args.test_size
        )

    print()
    print("=" * 80)
    print("Training Complete!")
    print("=" * 80)
    print()
    print("Metrics:")
    print(f"  Train R²: {metrics['train_r2']:.4f}")
    print(f"  Test R²:  {metrics['val_r2']:.4f}")
    print(f"  Test MAE: R$ {metrics['val_mae']:,.2f}")
    print(f"  Test RMSE: R$ {metrics['val_rmse']:,.2f}")
    print()

    # Feature importance (top 10)
    if "feature_importance" in metrics:
        print("Top 10 Feature Importances:")
        for item in sorted(
            metrics["feature_importance"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:
            print(f"  {item[0]}: {item[1]:.4f}")
        print()

    print(f"Model saved as: price_predictor_{args.version}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
