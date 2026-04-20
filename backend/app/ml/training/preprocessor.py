"""
Data Preprocessor - Prepare data for ML training
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class DataPreprocessor:
    """
    Preprocess data for ML training.

    Handles:
    - Missing value imputation
    - Feature scaling
    - Train/test split
    - Feature selection
    """

    def __init__(self):
        """Initialize DataPreprocessor"""
        self.scaler = None
        self.feature_columns = []
        self.is_fitted = False

    def preprocess_for_training(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Preprocess data and split into train/test sets.

        Args:
            df: Input DataFrame
            test_size: Fraction of data for testing
            random_state: Random seed

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Clean data
        df_clean = self._clean_data(df)

        # Handle missing values
        df_imputed = self._impute_missing(df_clean)

        # Remove outliers
        df_no_outliers = self._remove_outliers(df_imputed)

        # Split features and target
        y = df_no_outliers['price']
        X = df_no_outliers.drop(columns=['price'])

        # Store feature columns
        self.feature_columns = X.columns.tolist()

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state
        )

        # Fit scaler on training data only
        self.scaler = StandardScaler()
        numeric_cols = X_train.select_dtypes(include=[np.number]).columns
        X_train[numeric_cols] = self.scaler.fit_transform(X_train[numeric_cols])
        X_test[numeric_cols] = self.scaler.transform(X_test[numeric_cols])

        self.is_fitted = True

        return X_train, X_test, y_train, y_test

    def preprocess_for_prediction(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Preprocess data for prediction.

        Args:
            df: Input DataFrame

        Returns:
            Preprocessed DataFrame
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call preprocess_for_training first.")

        # Clean data
        df_clean = self._clean_data(df)

        # Handle missing values
        df_imputed = self._impute_missing(df_clean)

        # Remove outliers (optional for prediction)
        # df_no_outliers = self._remove_outliers(df_imputed)

        # Scale numeric columns
        numeric_cols = df_imputed.select_dtypes(include=[np.number]).columns
        if self.scaler and len(numeric_cols) > 0:
            # Only scale columns that were in training
            scale_cols = [col for col in numeric_cols if col in self.scaler.feature_names_in_]
            if scale_cols:
                df_imputed[scale_cols] = self.scaler.transform(df_imputed[scale_cols])

        return df_imputed

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data"""
        df = df.copy()

        # Remove rows with missing target
        df = df.dropna(subset=['price'])

        # Remove rows with price <= 0
        df = df[df['price'] > 0]

        # Remove rows with missing critical fields
        df = df.dropna(subset=['brand', 'model', 'model_year'])

        return df

    def _impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values"""
        df = df.copy()

        # Numeric: median imputation
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isna().sum() > 0:
                df[col] = df[col].fillna(df[col].median())

        # Categorical: mode imputation
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isna().sum() > 0:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "unknown")

        return df

    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers using IQR method"""
        df = df.copy()

        # Price outliers
        Q1 = df['price'].quantile(0.25)
        Q3 = df['price'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        df = df[(df['price'] >= lower_bound) & (df['price'] <= upper_bound)]

        # Mileage outliers
        if 'mileage' in df.columns:
            Q1 = df['mileage'].quantile(0.25)
            Q3 = df['mileage'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            df = df[(df['mileage'] >= lower_bound) & (df['mileage'] <= upper_bound)]

        return df

    def get_feature_columns(self) -> List[str]:
        """Get feature column names"""
        return self.feature_columns
