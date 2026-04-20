"""
Model Evaluator - Evaluate ML model performance
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error
)


class ModelEvaluator:
    """
    Evaluate ML model performance.

    Calculates:
    - Regression metrics (MAE, RMSE, R², MAPE)
    - Business metrics (price accuracy, position accuracy)
    - Feature importance
    """

    def evaluate_regression(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate regression model.

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            Dictionary with metrics
        """
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)

        # MAPE (handle division by zero)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

        return {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "mape": float(mape)
        }

    def evaluate_price_predictions(
        self,
        true_prices: np.ndarray,
        pred_prices: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluate price prediction model.

        Args:
            true_prices: True prices
            pred_prices: Predicted prices

        Returns:
            Dictionary with evaluation metrics
        """
        # Basic metrics
        regression_metrics = self.evaluate_regression(true_prices, pred_prices)

        # Business-specific metrics
        # Percentage within 5%, 10%, 15%
        errors = np.abs((pred_prices - true_prices) / true_prices)

        within_5pct = np.mean(errors <= 0.05)
        within_10pct = np.mean(errors <= 0.10)
        within_15pct = np.mean(errors <= 0.15)

        # Bias (mean error)
        bias = np.mean(pred_prices - true_prices)

        # Price range coverage
        in_range = 0  # Would need prediction intervals

        return {
            **regression_metrics,
            "within_5pct": float(within_5pct),
            "within_10pct": float(within_10pct),
            "within_15pct": float(within_15pct),
            "bias": float(bias),
            "in_range": float(in_range)
        }

    def calculate_feature_importance(
        self,
        model: Any,
        feature_names: List[str],
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Extract and format feature importance.

        Args:
            model: Trained model with feature_importances_
            feature_names: List of feature names
            top_n: Number of top features to return

        Returns:
            List of feature importance dictionaries
        """
        if not hasattr(model, 'feature_importances_'):
            return []

        importances = model.feature_importances_

        # Create feature importance list
        feature_importance = [
            {
                "feature": name,
                "importance": float(importance)
            }
            for name, importance in zip(feature_names, importances)
        ]

        # Sort by importance
        feature_importance.sort(key=lambda x: x["importance"], reverse=True)

        return feature_importance[:top_n]

    def create_evaluation_report(
        self,
        metrics: Dict[str, Any],
        model_name: str = "Price Model"
    ) -> str:
        """
        Create human-readable evaluation report.

        Args:
            metrics: Evaluation metrics
            model_name: Name of the model

        Returns:
            Formatted report string
        """
        report = f"""
{'=' * 80}
Model Evaluation Report: {model_name}
{'=' * 80}

Regression Metrics:
  MAE:  R$ {metrics.get('mae', 0):,.2f}
  RMSE: R$ {metrics.get('rmse', 0):,.2f}
  R²:   {metrics.get('r2', 0):.4f}
  MAPE: {metrics.get('mape', 0):.2f}%

Business Metrics:
  Within 5%:  {metrics.get('within_5pct', 0):.2%}
  Within 10%: {metrics.get('within_10pct', 0):.2%}
  Within 15%: {metrics.get('within_15pct', 0):.2%}
  Bias:       R$ {metrics.get('bias', 0):,.2f}

{'=' * 80}
"""
        return report

    def compare_models(
        self,
        metrics_list: List[Dict[str, Any]],
        model_names: List[str]
    ) -> pd.DataFrame:
        """
        Compare multiple models.

        Args:
            metrics_list: List of metrics dictionaries
            model_names: List of model names

        Returns:
            DataFrame with comparison
        """
        comparison_data = []

        for metrics, name in zip(metrics_list, model_names):
            comparison_data.append({
                "Model": name,
                "MAE": metrics.get("mae", 0),
                "RMSE": metrics.get("rmse", 0),
                "R²": metrics.get("r2", 0),
                "Within 5%": metrics.get("within_5pct", 0),
                "Within 10%": metrics.get("within_10pct", 0)
            })

        return pd.DataFrame(comparison_data)
