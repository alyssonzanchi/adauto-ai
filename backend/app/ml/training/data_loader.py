"""
Data Loader - Load and prepare training data
"""
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vehicle import Vehicle


class DataLoader:
    """
    Load training data from various sources.

    Supports:
    - Database (vehicles table)
    - CSV files
    - Parquet files
    - Synthetic data generation
    """

    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize DataLoader.

        Args:
            db_session: Optional database session
        """
        self.db_session = db_session

    async def load_from_db(
        self,
        limit: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Load vehicles from database.

        Args:
            limit: Optional limit on number of vehicles
            filters: Optional filters (status, brand, etc.)

        Returns:
            DataFrame with vehicle data
        """
        if not self.db_session:
            raise ValueError("Database session required")

        query = select(Vehicle)

        # Apply filters
        if filters:
            if "status" in filters:
                query = query.where(Vehicle.status == filters["status"])
            if "brand" in filters:
                query = query.where(Vehicle.brand == filters["brand"])

        # Apply limit
        if limit:
            query = query.limit(limit)

        # Execute query
        result = await self.db_session.execute(query)
        vehicles = result.scalars().all()

        # Convert to DataFrame
        data = []
        for vehicle in vehicles:
            data.append({
                "id": str(vehicle.id),
                "brand": vehicle.brand,
                "model": vehicle.model,
                "model_year": vehicle.model_year,
                "year": vehicle.year,
                "mileage": float(vehicle.mileage) if vehicle.mileage else 0,
                "color": vehicle.color or "",
                "transmission": vehicle.transmission or "",
                "fuel_type": vehicle.fuel_type or "",
                "body_type": vehicle.body_type or "",
                "doors": vehicle.doors or 4,
                "engine_capacity": float(vehicle.engine_capacity) if vehicle.engine_capacity else 2.0,
                "horsepower": float(vehicle.horsepower) if vehicle.horsepower else 150,
                "price": float(vehicle.price) if vehicle.price else 0,
                "status": vehicle.status or "available",
                "created_at": vehicle.created_at,
                "images": [img.url for img in vehicle.images] if vehicle.images else [],
                "features": vehicle.features or {},
                "dealership_id": str(vehicle.dealership_id) if vehicle.dealership_id else None
            })

        return pd.DataFrame(data)

    def load_from_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load data from CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            DataFrame with data
        """
        return pd.read_csv(file_path)

    def load_from_parquet(self, file_path: str) -> pd.DataFrame:
        """
        Load data from Parquet file.

        Args:
            file_path: Path to Parquet file

        Returns:
            DataFrame with data
        """
        return pd.read_parquet(file_path)

    def generate_synthetic_data(
        self,
        n_samples: int = 1000,
        random_seed: Optional[int] = 42
    ) -> pd.DataFrame:
        """
        Generate synthetic vehicle data for testing.

        Args:
            n_samples: Number of samples to generate
            random_seed: Random seed for reproducibility

        Returns:
            DataFrame with synthetic data
        """
        np.random.seed(random_seed)

        brands = ["Honda", "Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai", "Nissan"]
        models = ["Civic", "Corolla", "Jetta", "Onix", "Ka", "HB20", "Sentra"]
        body_types = ["sedan", "suv", "hatch", "pickup", "coupe"]
        fuel_types = ["gasoline", "flex", "diesel", "electric"]
        transmissions = ["manual", "automatic", "cvt"]
        colors = ["Branco", "Preto", "Prata", "Vermelho", "Azul", "Cinza"]

        data = []

        for _ in range(n_samples):
            brand = np.random.choice(brands)
            model_year = np.random.randint(2018, 2024)
            age_years = 2024 - model_year
            mileage = np.random.randint(0, 80000)

            # Base price by brand and year
            base_price = {
                "Honda": 90000,
                "Toyota": 95000,
                "Volkswagen": 85000,
                "Chevrolet": 75000,
                "Ford": 80000,
                "Hyundai": 70000,
                "Nissan": 75000
            }.get(brand, 80000)

            # Adjust for year
            price = base_price * (1 - 0.12 * age_years)
            price += np.random.normal(0, 5000)  # Add noise

            # Adjust for mileage
            price *= (1 - 0.001 * mileage / 1000)

            price = max(30000, price)  # Minimum price

            data.append({
                "brand": brand,
                "model": np.random.choice(models),
                "model_year": model_year,
                "year": model_year,
                "mileage": mileage,
                "color": np.random.choice(colors),
                "transmission": np.random.choice(transmissions, p=[0.3, 0.5, 0.2]),
                "fuel_type": np.random.choice(fuel_types, p=[0.3, 0.5, 0.1, 0.1]),
                "body_type": np.random.choice(body_types),
                "doors": np.random.choice([2, 4, 5], p=[0.1, 0.8, 0.1]),
                "engine_capacity": np.random.choice([1.0, 1.6, 2.0, 2.5, 3.0]),
                "horsepower": np.random.randint(80, 200),
                "price": round(price, 2),
                "status": np.random.choice(["available", "sold", "pending"], p=[0.6, 0.3, 0.1]),
                "images": [{"url": f"image{i}.jpg"} for i in range(np.random.randint(1, 6))],
                "features": {
                    "air_conditioning": np.random.choice([True, False], p=[0.9, 0.1]),
                    "power_windows": np.random.choice([True, False], p=[0.95, 0.05]),
                    "central_locking": np.random.choice([True, False], p=[0.9, 0.1]),
                    "cruise_control": np.random.choice([True, False], p=[0.7, 0.3]),
                    "sunroof": np.random.choice([True, False], p=[0.4, 0.6]),
                    "leather_seats": np.random.choice([True, False], p=[0.3, 0.7]),
                    "airbags": np.random.choice([True, False], p=[0.9, 0.1]),
                    "abs": np.random.choice([True, False], p=[0.95, 0.05]),
                    "bluetooth": np.random.choice([True, False], p=[0.85, 0.15]),
                    "usb": np.random.choice([True, False], p=[0.9, 0.1]),
                }
            })

        return pd.DataFrame(data)

    def create_training_set(
        self,
        df: pd.DataFrame,
        target_column: str = "price"
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create training set X, y from DataFrame.

        Args:
            df: Input DataFrame
            target_column: Name of target column

        Returns:
            Tuple of (X, y)
        """
        # Drop non-feature columns
        drop_cols = ["id", "created_at", "dealership_id"]
        df_features = df.drop(columns=[col for col in drop_cols if col in df.columns])

        # Separate features and target
        y = df_features[target_column]
        X = df_features.drop(columns=[target_column])

        return X, y
