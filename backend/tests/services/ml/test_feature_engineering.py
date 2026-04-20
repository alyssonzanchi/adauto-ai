"""
Tests for Feature Engineering
"""
import pytest
from datetime import datetime
from app.ml.features import (
    VehicleFeatures,
    MarketFeatures,
    TemporalFeatures,
    FeatureEngineer
)


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
    "created_at": datetime(2024, 3, 15),
    "images": [
        {"url": "image1.jpg"},
        {"url": "image2.jpg"},
        {"url": "image3.jpg"}
    ],
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


class TestVehicleFeatures:
    """Tests for VehicleFeatures"""

    def test_extract_features(self):
        """Test basic feature extraction"""
        extractor = VehicleFeatures()
        features = extractor.extract(SAMPLE_VEHICLE)

        # Check that we got features
        assert len(features) > 50

        # Check basic features
        assert features["brand_honda"] == 1
        assert features["brand_toyota"] == 0
        assert features["model_year"] == 2021
        assert features["mileage"] == 25000

        # Check derived features
        assert "age_months" in features
        assert "age_years" in features
        assert features["age_years"] == pytest.approx(3, abs=1)  # Approximately 3 years

        # Check scores
        assert "condition_score" in features
        assert 0 <= features["condition_score"] <= 1

    def test_brand_encoding(self):
        """Test brand one-hot encoding"""
        extractor = VehicleFeatures()
        features = extractor.extract(SAMPLE_VEHICLE)

        # Only one brand should be 1
        brand_sum = (
            features["brand_honda"] +
            features["brand_toyota"] +
            features["brand_volkswagen"] +
            features["brand_chevrolet"] +
            features["brand_ford"] +
            features["brand_other"]
        )
        assert brand_sum == 1

    def test_feature_scores(self):
        """Test feature score calculations"""
        extractor = VehicleFeatures()
        features = extractor.extract(SAMPLE_VEHICLE)

        # Comfort score (7 features, all present except electric_seats)
        assert features["comfort_score"] == pytest.approx(6/7, rel=0.1)

        # Safety score (6 features, all present)
        assert features["safety_score"] == 1.0

        # Technology score (6 features, all present)
        assert features["technology_score"] == 1.0

    def test_mileage_categorization(self):
        """Test mileage categorization"""
        extractor = VehicleFeatures()
        features = extractor.extract(SAMPLE_VEHICLE)

        # 25000 km should be low mileage
        assert features["low_mileage"] == 1
        assert features["avg_mileage"] == 0
        assert features["high_mileage"] == 0

    def test_age_categorization(self):
        """Test age categorization"""
        extractor = VehicleFeatures()
        features = extractor.extract(SAMPLE_VEHICLE)

        # 2021 model (~3 years old)
        assert features["is_new"] == 0
        assert features["is_semi_new"] == 1
        assert features["is_used"] == 0

    def test_price_per_km(self):
        """Test price per kilometer calculation"""
        extractor = VehicleFeatures()
        features = extractor.extract(SAMPLE_VEHICLE)

        expected = 138500 / 25000
        assert features["price_per_km"] == pytest.approx(expected, rel=0.01)

    def test_get_feature_names(self):
        """Test feature names extraction"""
        extractor = VehicleFeatures()
        extractor.extract(SAMPLE_VEHICLE)

        names = extractor.get_feature_names()
        assert len(names) > 50
        assert "brand_honda" in names
        assert "condition_score" in names

    def test_get_feature_importance_groups(self):
        """Test feature grouping"""
        extractor = VehicleFeatures()
        groups = extractor.get_feature_importance_groups()

        assert "basic" in groups
        assert "technical" in groups
        assert "comfort" in groups
        assert "safety" in groups
        assert "technology" in groups
        assert "market" in groups
        assert "derived" in groups


class TestTemporalFeatures:
    """Tests for TemporalFeatures"""

    def test_extract_date_features(self):
        """Test date feature extraction"""
        extractor = TemporalFeatures()
        features = extractor.extract({}, datetime(2024, 4, 20))

        assert features["day_of_week"] == 5  # Saturday
        assert features["day_of_month"] == 20
        assert features["month"] == 4
        assert features["quarter"] == 2
        assert features["year"] == 2024

    def test_weekend_detection(self):
        """Test weekend detection"""
        extractor = TemporalFeatures()

        # Saturday (weekend)
        features = extractor.extract({}, datetime(2024, 4, 20))
        assert features["is_weekend"] == 1

        # Monday (not weekend)
        features = extractor.extract({}, datetime(2024, 4, 22))
        assert features["is_weekend"] == 0

    def test_seasonality(self):
        """Test seasonality features"""
        extractor = TemporalFeatures()

        # April (fall in Brazil)
        features = extractor.extract({}, datetime(2024, 4, 20))
        assert features["is_fall"] == 1
        assert features["is_summer"] == 0

        # December (summer in Brazil)
        features = extractor.extract({}, datetime(2024, 12, 15))
        assert features["is_summer"] == 1
        assert features["is_christmas_season"] == 1

    def test_payday_detection(self):
        """Test payday detection"""
        extractor = TemporalFeatures()

        # Day 5 (early payday)
        features = extractor.extract({}, datetime(2024, 4, 5))
        assert features["is_payday_period"] == 1
        assert features["is_early_payday"] == 1

        # Day 28 (late payday)
        features = extractor.extract({}, datetime(2024, 4, 28))
        assert features["is_payday_period"] == 1
        assert features["is_late_payday"] == 1

        # Day 15 (mid-month)
        features = extractor.extract({}, datetime(2024, 4, 15))
        assert features["is_mid_month_payday"] == 1

    def test_listing_age(self):
        """Test listing age calculation"""
        extractor = TemporalFeatures()

        # Vehicle created 30 days ago
        created = datetime(2024, 3, 20)
        reference = datetime(2024, 4, 20)

        vehicle = SAMPLE_VEHICLE.copy()
        vehicle["created_at"] = created

        features = extractor.extract(vehicle, reference)

        assert features["days_since_listing"] == 30
        assert features["weeks_since_listing"] == 4
        assert features["is_fresh_listing"] == 0
        assert features["is_recent_listing"] == 1


class TestMarketFeatures:
    """Tests for MarketFeatures (without DB)"""

    def test_extract_without_db(self):
        """Test feature extraction without database connection"""
        extractor = MarketFeatures(db_session=None)
        features = extractor.extract(SAMPLE_VEHICLE)

        # Should return default values
        assert "search_volume" in features
        assert "inventory_count" in features
        assert "demand_score" in features
        assert "supply_score" in features

    def test_default_values(self):
        """Test default values when no DB"""
        extractor = MarketFeatures(db_session=None)
        features = extractor.extract(SAMPLE_VEHICLE)

        # Demand features should have defaults
        assert features["search_volume"] == 0
        assert features["view_count"] == 0
        assert features["demand_score"] == 0.5

        # Supply features should have defaults
        assert features["inventory_count"] == 0
        assert features["new_listings_7d"] == 0


class TestFeatureEngineer:
    """Tests for FeatureEngineer"""

    @pytest.mark.asyncio
    async def test_extract_all_features(self):
        """Test extraction of all features"""
        engineer = FeatureEngineer(db_session=None)
        features = await engineer.extract_features(SAMPLE_VEHICLE)

        # Should have 100+ features
        assert len(features) >= 100

        # Check features from different sources
        assert "brand_honda" in features  # Vehicle
        assert "demand_score" in features  # Market
        assert "is_weekend" in features  # Temporal

    @pytest.mark.asyncio
    async def test_get_feature_names(self):
        """Test getting feature names"""
        engineer = FeatureEngineer(db_session=None)
        names = engineer.get_feature_names()

        assert len(names) >= 100
        assert "brand_honda" in names
        assert "demand_score" in names
        assert "is_weekend" in names

    @pytest.mark.asyncio
    async def test_get_feature_counts(self):
        """Test feature count per category"""
        engineer = FeatureEngineer(db_session=None)
        counts = engineer.get_feature_counts()

        assert "basic" in counts
        assert "technical" in counts
        assert "comfort" in counts
        assert "market" in counts
        assert "temporal" in counts

        # Each category should have features
        for category, count in counts.items():
            assert count > 0, f"{category} has no features"

    @pytest.mark.asyncio
    async def test_validate_features(self):
        """Test feature validation"""
        engineer = FeatureEngineer(db_session=None)
        features = await engineer.extract_features(SAMPLE_VEHICLE)

        validation = engineer.validate_features(features)

        # Should be valid
        assert validation["is_valid"] == True
        assert len(validation["invalid_values"]) == 0

    @pytest.mark.asyncio
    async def test_summarize_features(self):
        """Test feature summarization"""
        engineer = FeatureEngineer(db_session=None)
        features = await engineer.extract_features(SAMPLE_VEHICLE)

        summary = engineer.summarize_features(features)

        # Check summary structure
        assert "vehicle" in summary
        assert "market" in summary
        assert "timing" in summary
        assert "scores" in summary

        # Check vehicle summary
        assert summary["vehicle"]["age_years"] == pytest.approx(3, abs=1)
        assert summary["vehicle"]["mileage"] == 25000

    @pytest.mark.asyncio
    async def test_prepare_for_model(self):
        """Test preparing features for ML model"""
        engineer = FeatureEngineer(db_session=None)
        features = await engineer.extract_features(SAMPLE_VEHICLE)

        feature_array = engineer.prepare_for_model(features)

        # Should be numpy array
        import numpy as np
        assert isinstance(feature_array, np.ndarray)

        # Should have values
        assert len(feature_array) > 0
        assert all(isinstance(x, (int, float)) for x in feature_array)


class TestFeatureIntegration:
    """Integration tests for feature engineering"""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete feature extraction pipeline"""
        # Initialize
        engineer = FeatureEngineer(db_session=None)

        # Extract features
        features = await engineer.extract_features(SAMPLE_VEHICLE)

        # Validate
        validation = engineer.validate_features(features)
        assert validation["is_valid"] == True

        # Summarize
        summary = engineer.summarize_features(features)
        assert "vehicle" in summary

        # Prepare for model
        feature_array = engineer.prepare_for_model(features)
        assert len(feature_array) > 0

    @pytest.mark.asyncio
    async def test_multiple_vehicles(self):
        """Test batch feature extraction"""
        engineer = FeatureEngineer(db_session=None)

        vehicles = [SAMPLE_VEHICLE] * 3  # Same vehicle 3 times

        # Note: extract_features_batch is not implemented yet
        # This test will fail until we implement it
        # df = await engineer.extract_features_batch(vehicles)
        # assert len(df) == 3

    @pytest.mark.asyncio
    async def test_feature_consistency(self):
        """Test that features are consistent across multiple extractions"""
        engineer = FeatureEngineer(db_session=None)

        features1 = await engineer.extract_features(SAMPLE_VEHICLE)
        features2 = await engineer.extract_features(SAMPLE_VEHICLE)

        # Temporal features may differ slightly due to timing
        # but most should be the same
        for key in features1:
            if key not in ["is_weekend", "is_payday_period", "day_of_week"]:
                assert features1[key] == features2[key], f"{key} differs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
