"""
Tests for Price Model
"""
import pytest
import numpy as np
from app.services.ml.price_model import PriceModel
from app.services.ml.model_registry import ModelRegistry


# Sample vehicle data
SAMPLE_VEHICLE = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "brand": "Honda",
    "model": "Civic Touring",
    "model_year": 2021,
    "year": 2021,
    "mileage": 25000,
    "color": "Branco",
    "transmission": "CVT",
    "fuel_type": "flex",
    "body_type": "sedan",
    "doors": 4,
    "engine_capacity": 2.0,
    "horsepower": 173,
    "price": 138500.00,
    "status": "available",
    "created_at": "2024-03-15T00:00:00",
    "images": [{"url": "image1.jpg"}],
    "features": {
        "air_conditioning": True,
        "power_windows": True,
        "central_locking": True,
        "cruise_control": True,
        "sunroof": True,
        "leather_seats": True,
        "electric_seats": False,
        "airbags": True,
        "abs": True,
        "esp": True,
        "traction_control": True,
        "rear_camera": True,
        "parking_sensors": True,
        "bluetooth": True,
        "usb": True,
        "android_auto": True,
        "apple_carplay": True,
        "navigation": True,
        "premium_sound": True
    },
    "dealership_id": "dealership-uuid-123"
}


class TestPriceModel:
    """Tests for PriceModel"""

    @pytest.mark.asyncio
    async def test_predict_fallback(self):
        """Test prediction with fallback (no trained model)"""
        model = PriceModel()
        prediction = await model.predict(SAMPLE_VEHICLE)

        # Check structure
        assert "predicted_price" in prediction
        assert "price_range" in prediction
        assert "price_score" in prediction
        assert "price_position" in prediction
        assert "confidence" in prediction

        # Check types
        assert isinstance(prediction["predicted_price"], (int, float))
        assert isinstance(prediction["price_range"], list)
        assert len(prediction["price_range"]) == 2
        assert isinstance(prediction["price_score"], int)
        assert isinstance(prediction["price_position"], str)
        assert isinstance(prediction["confidence"], float)

        # Check ranges
        assert 0 <= prediction["price_score"] <= 100
        assert 0 <= prediction["confidence"] <= 1
        assert prediction["price_range"][0] < prediction["price_range"][1]

    @pytest.mark.asyncio
    async def test_price_position_categories(self):
        """Test price position categorization"""
        model = PriceModel()

        # Great deal (price much lower than predicted)
        vehicle_cheap = SAMPLE_VEHICLE.copy()
        vehicle_cheap["price"] = 100000
        prediction = await model.predict(vehicle_cheap)
        assert prediction["price_position"] in ["great_deal", "good_price"]

        # Overpriced (price much higher than predicted)
        vehicle_expensive = SAMPLE_VEHICLE.copy()
        vehicle_expensive["price"] = 200000
        prediction = await model.predict(vehicle_expensive)
        assert prediction["price_position"] in ["expensive", "overpriced"]

    @pytest.mark.asyncio
    async def test_batch_predictions(self):
        """Test batch predictions"""
        model = PriceModel()

        vehicles = [SAMPLE_VEHICLE] * 3
        predictions = await model.predict_batch(vehicles)

        assert len(predictions) == 3
        for pred in predictions:
            assert "predicted_price" in pred

    def test_calculate_price_score(self):
        """Test price score calculation"""
        model = PriceModel()

        # Fair price (same as predicted)
        score, position = model._calculate_price_score(100000, 100000)
        assert score == 50
        assert position == "fair_price"

        # Good deal (15% below)
        score, position = model._calculate_price_score(85000, 100000)
        assert score > 50
        assert position == "good_price"

        # Overpriced (15% above)
        score, position = model._calculate_price_score(115000, 100000)
        assert score < 50
        assert position == "expensive"

    def test_calculate_confidence(self):
        """Test confidence calculation"""
        model = PriceModel()

        # High confidence features
        good_features = {
            "age_years": 2,
            "mileage": 20000,
            "condition_score": 0.8,
            "demand_score": 0.7,
            "supply_score": 0.6
        }
        confidence = model._calculate_confidence(good_features)
        assert confidence > 0.7

        # Low confidence features
        bad_features = {
            "age_years": 15,
            "mileage": 150000,
            "condition_score": 0.3,
            "demand_score": 0,
            "supply_score": 0
        }
        confidence = model._calculate_confidence(bad_features)
        assert confidence < 0.7


class TestModelRegistry:
    """Tests for ModelRegistry"""

    def test_register_and_load_model(self):
        """Test model registration and loading"""
        registry = ModelRegistry("backend/app/ml/models/test")

        # Create a simple model
        from sklearn.dummy import DummyRegressor
        model = DummyRegressor()
        model.fit([[1]], [100])

        # Register model
        metadata = {
            "model_type": "test",
            "accuracy": 0.95
        }

        success = registry.register_model(
            "test_model",
            "1.0.0",
            model,
            metadata
        )
        assert success

        # Load model
        loaded = registry.load_model("test_model", "1.0.0")
        assert loaded is not None
        assert loaded["metadata"]["model_type"] == "test"

    def test_list_models(self):
        """Test listing models"""
        registry = ModelRegistry("backend/app/ml/models/test")

        models = registry.list_models()
        assert isinstance(models, list)

    def test_get_latest_version(self):
        """Test getting latest version"""
        registry = ModelRegistry("backend/app/ml/models/test")

        # Register multiple versions
        from sklearn.dummy import DummyRegressor

        for version in ["1.0.0", "1.1.0", "2.0.0"]:
            model = DummyRegressor()
            model.fit([[1]], [100])
            registry.register_model("versioned_model", version, model, {})

        # Get latest
        latest = registry.get_latest_version("versioned_model")
        assert latest == "2.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
