"""
Vehicle Features - Extracts 50+ features from vehicle data
"""
from datetime import datetime, date
from typing import Dict, Any, Optional
from decimal import Decimal


class VehicleFeatures:
    """
    Extracts comprehensive features from vehicle data for ML models.

    Features categories:
    - Basic: brand, model, year, mileage, color
    - Technical: transmission, fuel_type, body_type, doors, engine
    - Comfort: air_conditioning, power_windows, central_locking
    - Safety: airbags, abs, esp, rear_camera
    - Technology: bluetooth, usb, android_auto, apple_carplay
    - Market: price, price_per_km, depreciation_rate, days_on_market
    """

    def __init__(self):
        self.feature_names = []

    def extract(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all features from vehicle data.

        Args:
            vehicle_data: Dictionary with vehicle information

        Returns:
            Dictionary with 50+ extracted features
        """
        features = {}

        # Basic features (15)
        features.update(self._extract_basic_features(vehicle_data))

        # Technical features (12)
        features.update(self._extract_technical_features(vehicle_data))

        # Comfort features (8)
        features.update(self._extract_comfort_features(vehicle_data))

        # Safety features (6)
        features.update(self._extract_safety_features(vehicle_data))

        # Technology features (6)
        features.update(self._extract_technology_features(vehicle_data))

        # Market features (10)
        features.update(self._extract_market_features(vehicle_data))

        # Derived features (15+)
        features.update(self._extract_derived_features(vehicle_data, features))

        self.feature_names = list(features.keys())
        return features

    def _extract_basic_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic vehicle features"""
        features = {}

        # Brand encoding (one-hot style)
        brand = data.get("brand", "")
        features["brand_honda"] = 1 if brand.lower() == "honda" else 0
        features["brand_toyota"] = 1 if brand.lower() == "toyota" else 0
        features["brand_volkswagen"] = 1 if brand.lower() == "volkswagen" else 0
        features["brand_chevrolet"] = 1 if brand.lower() == "chevrolet" else 0
        features["brand_ford"] = 1 if brand.lower() == "ford" else 0
        features["brand_other"] = 1 if brand.lower() not in ["honda", "toyota", "volkswagen", "chevrolet", "ford"] else 0

        # Model info
        features["model_year"] = int(data.get("model_year", 2020))
        features["year"] = int(data.get("year", 2024))

        # Mileage
        mileage = data.get("mileage", 0)
        features["mileage"] = float(mileage) if mileage else 0.0

        # Color
        color = data.get("color", "").lower()
        features["color_white"] = 1 if color in ["branco", "white"] else 0
        features["color_black"] = 1 if color in ["preto", "black"] else 0
        features["color_silver"] = 1 if color in ["prata", "silver", "cinza"] else 0
        features["color_red"] = 1 if color in ["vermelho", "red"] else 0
        features["color_other"] = 1 if color not in ["branco", "white", "preto", "black", "prata", "silver", "cinza", "vermelho", "red"] else 0

        return features

    def _extract_technical_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical vehicle features"""
        features = {}

        # Transmission
        transmission = data.get("transmission", "manual").lower()
        features["transmission_automatic"] = 1 if "automatic" in transmission or "cv" in transmission else 0
        features["transmission_manual"] = 1 if transmission == "manual" else 0

        # Fuel type
        fuel_type = data.get("fuel_type", "gasoline").lower()
        features["fuel_flex"] = 1 if fuel_type in ["flex", "flexfuel"] else 0
        features["fuel_gasoline"] = 1 if fuel_type in ["gasoline", "gasolina"] else 0
        features["fuel_diesel"] = 1 if fuel_type == "diesel" else 0
        features["fuel_electric"] = 1 if fuel_type in ["electric", "elétrico", "hibrido"] else 0

        # Body type
        body_type = data.get("body_type", "sedan").lower()
        features["body_sedan"] = 1 if body_type == "sedan" else 0
        features["body_suv"] = 1 if body_type in ["suv", "utilitario"] else 0
        features["body_hatch"] = 1 if body_type in ["hatch", "hatchback"] else 0
        features["body_pickup"] = 1 if body_type == "pickup" else 0
        features["body_coupe"] = 1 if body_type in ["coupe", "cupidê"] else 0
        features["body_wagon"] = 1 if body_type in ["wagon", "perua"] else 0

        # Doors
        features["doors"] = int(data.get("doors", 4))

        # Engine
        features["engine_capacity"] = float(data.get("engine_capacity", 2.0))  # Liters
        features["horsepower"] = float(data.get("horsepower", 150))  # HP

        return features

    def _extract_comfort_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comfort features"""
        features = {}
        features_data = data.get("features", {})

        features["has_air_conditioning"] = 1 if features_data.get("air_conditioning") else 0
        features["has_power_windows"] = 1 if features_data.get("power_windows") else 0
        features["has_central_locking"] = 1 if features_data.get("central_locking") else 0
        features["has_cruise_control"] = 1 if features_data.get("cruise_control") else 0
        features["has_sunroof"] = 1 if features_data.get("sunroof") else 0
        features["has_leather_seats"] = 1 if features_data.get("leather_seats") else 0
        features["has_electric_seats"] = 1 if features_data.get("electric_seats") else 0
        features["comfort_score"] = sum([
            features["has_air_conditioning"],
            features["has_power_windows"],
            features["has_central_locking"],
            features["has_cruise_control"],
            features["has_sunroof"],
            features["has_leather_seats"],
            features["has_electric_seats"],
        ]) / 7.0  # Normalizado 0-1

        return features

    def _extract_safety_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract safety features"""
        features = {}
        features_data = data.get("features", {})

        features["has_airbags"] = 1 if features_data.get("airbags") else 0
        features["has_abs"] = 1 if features_data.get("abs") else 0
        features["has_esp"] = 1 if features_data.get("esp") else 0
        features["has_traction_control"] = 1 if features_data.get("traction_control") else 0
        features["has_rear_camera"] = 1 if features_data.get("rear_camera") else 0
        features["has_parking_sensors"] = 1 if features_data.get("parking_sensors") else 0
        features["safety_score"] = sum([
            features["has_airbags"],
            features["has_abs"],
            features["has_esp"],
            features["has_traction_control"],
            features["has_rear_camera"],
            features["has_parking_sensors"],
        ]) / 6.0  # Normalizado 0-1

        return features

    def _extract_technology_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technology features"""
        features = {}
        features_data = data.get("features", {})

        features["has_bluetooth"] = 1 if features_data.get("bluetooth") else 0
        features["has_usb"] = 1 if features_data.get("usb") else 0
        features["has_android_auto"] = 1 if features_data.get("android_auto") else 0
        features["has_apple_carplay"] = 1 if features_data.get("apple_carplay") else 0
        features["has_navigation"] = 1 if features_data.get("navigation") else 0
        features["has_premium_sound"] = 1 if features_data.get("premium_sound") else 0
        features["technology_score"] = sum([
            features["has_bluetooth"],
            features["has_usb"],
            features["has_android_auto"],
            features["has_apple_carplay"],
            features["has_navigation"],
            features["has_premium_sound"],
        ]) / 6.0  # Normalizado 0-1

        return features

    def _extract_market_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market-related features"""
        features = {}

        # Price
        price = data.get("price", 0)
        features["price"] = float(price) if price else 0.0

        # Status
        status = data.get("status", "available").lower()
        features["is_available"] = 1 if status == "available" else 0
        features["is_sold"] = 1 if status == "sold" else 0
        features["is_reserved"] = 1 if status == "reserved" else 0
        features["is_pending"] = 1 if status == "pending" else 0

        # Images
        images = data.get("images", [])
        features["image_count"] = len(images) if images else 0

        # Days on market
        created_at = data.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            elif not isinstance(created_at, datetime):
                created_at = datetime.combine(created_at, datetime.min.time())
            features["days_on_market"] = (datetime.now() - created_at).days
        else:
            features["days_on_market"] = 0

        return features

    def _extract_derived_features(self, data: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Extract derived/computed features"""
        derived = {}

        # Age calculations
        current_year = datetime.now().year
        model_year = features.get("model_year", 2020)
        derived["age_months"] = (current_year - model_year) * 12
        derived["age_years"] = current_year - model_year
        derived["is_new"] = 1 if derived["age_years"] <= 1 else 0
        derived["is_semi_new"] = 1 if 1 < derived["age_years"] <= 3 else 0
        derived["is_used"] = 1 if derived["age_years"] > 3 else 0

        # Mileage calculations
        mileage = features.get("mileage", 0)
        if derived["age_months"] > 0:
            derived["mileage_per_year"] = (mileage / derived["age_months"]) * 12
        else:
            derived["mileage_per_year"] = 0
        derived["low_mileage"] = 1 if mileage < 30000 else 0
        derived["avg_mileage"] = 1 if 30000 <= mileage < 60000 else 0
        derived["high_mileage"] = 1 if mileage >= 60000 else 0

        # Price calculations
        price = features.get("price", 0)
        if mileage > 0:
            derived["price_per_km"] = price / mileage
        else:
            derived["price_per_km"] = 0

        # Depreciation (simplified - assumes 15% per year)
        derived["depreciation_rate"] = min(0.15 * derived["age_years"], 0.70)  # Max 70%
        derived["estimated_new_price"] = price / (1 - derived["depreciation_rate"]) if derived["depreciation_rate"] < 1 else price

        # Feature richness
        derived["feature_score"] = (
            features.get("comfort_score", 0) * 0.3 +
            features.get("safety_score", 0) * 0.4 +
            features.get("technology_score", 0) * 0.3
        )

        # Body type preference (based on market trends)
        derived["is_body_type_popular"] = 1 if features.get("body_suv") or features.get("body_sedan") else 0

        # Fuel efficiency preference
        derived["is_fuel_efficient"] = 1 if features.get("fuel_flex") or features.get("fuel_electric") else 0

        # Transmission preference
        derived["is_transmission_preferred"] = features.get("transmission_automatic", 0)

        # Color premium
        derived["is_color_premium"] = 1 if features.get("color_white") or features.get("color_black") else 0

        # Overall condition score (weighted)
        derived["condition_score"] = (
            (1.0 - min(mileage / 100000, 1.0)) * 0.4 +  # Mileage impact
            (1.0 - min(derived["age_years"] / 10, 1.0)) * 0.3 +  # Age impact
            derived["feature_score"] * 0.3  # Features impact
        )

        return derived

    def get_feature_names(self) -> list:
        """Return list of feature names"""
        return self.feature_names

    def get_feature_importance_groups(self) -> Dict[str, list]:
        """
        Return feature names grouped by category for interpretation.

        Returns:
            Dictionary mapping category names to lists of feature names
        """
        return {
            "basic": [
                "brand_honda", "brand_toyota", "brand_volkswagen",
                "brand_chevrolet", "brand_ford", "brand_other",
                "model_year", "year", "mileage",
                "color_white", "color_black", "color_silver", "color_red", "color_other"
            ],
            "technical": [
                "transmission_automatic", "transmission_manual",
                "fuel_flex", "fuel_gasoline", "fuel_diesel", "fuel_electric",
                "body_sedan", "body_suv", "body_hatch", "body_pickup",
                "body_coupe", "body_wagon", "doors", "engine_capacity", "horsepower"
            ],
            "comfort": [
                "has_air_conditioning", "has_power_windows",
                "has_central_locking", "has_cruise_control",
                "has_sunroof", "has_leather_seats", "has_electric_seats",
                "comfort_score"
            ],
            "safety": [
                "has_airbags", "has_abs", "has_esp",
                "has_traction_control", "has_rear_camera",
                "has_parking_sensors", "safety_score"
            ],
            "technology": [
                "has_bluetooth", "has_usb", "has_android_auto",
                "has_apple_carplay", "has_navigation", "has_premium_sound",
                "technology_score"
            ],
            "market": [
                "price", "is_available", "is_sold", "is_reserved",
                "is_pending", "image_count", "days_on_market"
            ],
            "derived": [
                "age_months", "age_years", "is_new", "is_semi_new", "is_used",
                "mileage_per_year", "low_mileage", "avg_mileage", "high_mileage",
                "price_per_km", "depreciation_rate", "estimated_new_price",
                "feature_score", "is_body_type_popular", "is_fuel_efficient",
                "is_transmission_preferred", "is_color_premium", "condition_score"
            ]
        }
