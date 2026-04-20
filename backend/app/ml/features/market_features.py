"""
Market Features - Extracts market-related features
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class MarketFeatures:
    """
    Extracts market-related features for ML models.

    Features categories:
    - Demand: search_volume, view_count, lead_count
    - Supply: inventory_count, new_listings, similar_count
    - Seasonality: month, quarter, is_holiday_season
    - Trends: price_change_30d, price_change_90d
    - Geography: region_price_index, demand_by_state
    """

    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize MarketFeatures.

        Args:
            db_session: Optional database session for dynamic features
        """
        self.db_session = db_session
        self.feature_names = []

    async def extract(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all market features.

        Args:
            vehicle_data: Dictionary with vehicle information

        Returns:
            Dictionary with market features
        """
        features = {}

        # Demand features (5)
        features.update(await self._extract_demand_features(vehicle_data))

        # Supply features (5)
        features.update(await self._extract_supply_features(vehicle_data))

        # Seasonality features (6)
        features.update(self._extract_seasonality_features(vehicle_data))

        # Trend features (4)
        features.update(await self._extract_trend_features(vehicle_data))

        # Geography features (3)
        features.update(await self._extract_geography_features(vehicle_data))

        # Competition features (3)
        features.update(await self._extract_competition_features(vehicle_data))

        self.feature_names = list(features.keys())
        return features

    async def _extract_demand_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract demand-related features"""
        features = {}

        if not self.db_session:
            # Return default/placeholder values if no DB session
            features["search_volume"] = 0
            features["view_count"] = 0
            features["lead_count"] = 0
            features["demand_score"] = 0.5  # Medium demand
            features["is_high_demand"] = 0
            return features

        # Get model/brand for queries
        brand = data.get("brand", "")
        model = data.get("model", "")
        body_type = data.get("body_type", "")

        # Search volume (simulated - in production would use analytics)
        query = text("""
            SELECT COUNT(*) as count
            FROM vehicle_views vv
            JOIN vehicles v ON vv.vehicle_id = v.id
            WHERE v.brand = :brand
            AND v.model = :model
            AND vv.created_at > NOW() - INTERVAL '30 days'
        """)

        try:
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model
            })
            features["search_volume"] = result.scalar() or 0
        except Exception:
            features["search_volume"] = 0

        # View count (similar vehicle views in last 30 days)
        query = text("""
            SELECT COUNT(*) as count
            FROM vehicle_views
            WHERE vehicle_id IN (
                SELECT id FROM vehicles
                WHERE brand = :brand
                AND model = :model
                AND created_at > NOW() - INTERVAL '2 years'
            )
            AND created_at > NOW() - INTERVAL '30 days'
        """)

        try:
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model
            })
            features["view_count"] = result.scalar() or 0
        except Exception:
            features["view_count"] = 0

        # Lead count (leads for similar vehicles)
        query = text("""
            SELECT COUNT(*) as count
            FROM leads l
            JOIN vehicles v ON l.vehicle_id = v.id
            WHERE v.brand = :brand
            AND v.model = :model
            AND l.created_at > NOW() - INTERVAL '30 days'
        """)

        try:
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model
            })
            features["lead_count"] = result.scalar() or 0
        except Exception:
            features["lead_count"] = 0

        # Demand score (normalized 0-1)
        # In production, would use more sophisticated calculation
        max_views = 1000  # Threshold for "high demand"
        features["demand_score"] = min(features["view_count"] / max_views, 1.0)
        features["is_high_demand"] = 1 if features["demand_score"] > 0.7 else 0

        return features

    async def _extract_supply_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract supply-related features"""
        features = {}

        if not self.db_session:
            # Return default values
            features["inventory_count"] = 0
            features["new_listings_7d"] = 0
            features["new_listings_30d"] = 0
            features["supply_score"] = 0.5
            features["is_low_supply"] = 0
            return features

        brand = data.get("brand", "")
        model = data.get("model", "")

        # Current inventory (available vehicles of same model)
        query = text("""
            SELECT COUNT(*) as count
            FROM vehicles
            WHERE brand = :brand
            AND model = :model
            AND status = 'available'
            AND created_at > NOW() - INTERVAL '6 months'
        """)

        try:
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model
            })
            features["inventory_count"] = result.scalar() or 0
        except Exception:
            features["inventory_count"] = 0

        # New listings (last 7 days)
        query = text("""
            SELECT COUNT(*) as count
            FROM vehicles
            WHERE brand = :brand
            AND model = :model
            AND created_at > NOW() - INTERVAL '7 days'
        """)

        try:
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model
            })
            features["new_listings_7d"] = result.scalar() or 0
        except Exception:
            features["new_listings_7d"] = 0

        # New listings (last 30 days)
        query = text("""
            SELECT COUNT(*) as count
            FROM vehicles
            WHERE brand = :brand
            AND model = :model
            AND created_at > NOW() - INTERVAL '30 days'
        """)

        try:
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model
            })
            features["new_listings_30d"] = result.scalar() or 0
        except Exception:
            features["new_listings_30d"] = 0

        # Supply score (inverse - fewer vehicles = higher score)
        max_inventory = 100  # Threshold for "high supply"
        features["supply_score"] = 1.0 - min(features["inventory_count"] / max_inventory, 1.0)
        features["is_low_supply"] = 1 if features["supply_score"] > 0.7 else 0

        return features

    def _extract_seasonality_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract seasonality features"""
        features = {}
        now = datetime.now()

        # Time-based features
        features["month"] = now.month
        features["quarter"] = (now.month - 1) // 3 + 1
        features["day_of_week"] = now.weekday()  # 0=Monday, 6=Sunday
        features["is_weekend"] = 1 if now.weekday() >= 5 else 0

        # Season features
        month = now.month
        features["is_summer"] = 1 if month in [12, 1, 2] else 0  # Brazil summer
        features["is_winter"] = 1 if month in [6, 7, 8] else 0  # Brazil winter
        features["is_spring"] = 1 if month in [9, 10, 11] else 0
        features["is_fall"] = 1 if month in [3, 4, 5] else 0

        # Holiday seasons (Brazil)
        features["is_holiday_season"] = 1 if month in [12, 1] else 0  # Christmas/New Year
        features["is_year_end"] = 1 if month == 12 else 0
        features["is_year_start"] = 1 if month == 1 else 0

        # Payday periods (simplified)
        features["is_payday_period"] = 1 if now.day in [1, 2, 3, 30, 31] else 0

        return features

    async def _extract_trend_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract price trend features"""
        features = {}

        if not self.db_session:
            # Return default values
            features["price_change_30d"] = 0.0
            features["price_change_90d"] = 0.0
            features["price_trend_up"] = 0
            features["price_trend_down"] = 0
            return features

        brand = data.get("brand", "")
        model = data.get("model", "")
        current_price = data.get("price", 0)

        if current_price == 0:
            features["price_change_30d"] = 0.0
            features["price_change_90d"] = 0.0
            features["price_trend_up"] = 0
            features["price_trend_down"] = 0
            return features

        # Average price 30 days ago
        query = text("""
            SELECT COALESCE(AVG(price), 0) as avg_price
            FROM vehicles
            WHERE brand = :brand
            AND model = :model
            AND created_at BETWEEN
                NOW() - INTERVAL '60 days' AND
                NOW() - INTERVAL '30 days'
            AND status = 'sold'
        """)

        try:
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model
            })
            avg_price_30d_ago = result.scalar() or 0

            if avg_price_30d_ago > 0:
                features["price_change_30d"] = (current_price - avg_price_30d_ago) / avg_price_30d_ago
            else:
                features["price_change_30d"] = 0.0
        except Exception:
            features["price_change_30d"] = 0.0

        # Average price 90 days ago
        query = text("""
            SELECT COALESCE(AVG(price), 0) as avg_price
            FROM vehicles
            WHERE brand = :brand
            AND model = :model
            AND created_at BETWEEN
                NOW() - INTERVAL '120 days' AND
                NOW() - INTERVAL '90 days'
            AND status = 'sold'
        """)

        try:
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model
            })
            avg_price_90d_ago = result.scalar() or 0

            if avg_price_90d_ago > 0:
                features["price_change_90d"] = (current_price - avg_price_90d_ago) / avg_price_90d_ago
            else:
                features["price_change_90d"] = 0.0
        except Exception:
            features["price_change_90d"] = 0.0

        # Trend indicators
        features["price_trend_up"] = 1 if features["price_change_30d"] > 0.05 else 0
        features["price_trend_down"] = 1 if features["price_change_30d"] < -0.05 else 0

        return features

    async def _extract_geography_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract geography-based features"""
        features = {}

        if not self.db_session:
            # Return default values
            features["region_price_index"] = 1.0
            features["demand_by_state"] = 0.5
            features["is_metro_area"] = 0
            return features

        # Get dealership location
        dealership_id = data.get("dealership_id")

        if not dealership_id:
            features["region_price_index"] = 1.0
            features["demand_by_state"] = 0.5
            features["is_metro_area"] = 0
            return features

        # Get dealership state
        query = text("""
            SELECT state, city
            FROM dealerships
            WHERE id = :dealership_id
        """)

        try:
            result = await self.db_session.execute(query, {
                "dealership_id": dealership_id
            })
            row = result.fetchone()

            if not row:
                features["region_price_index"] = 1.0
                features["demand_by_state"] = 0.5
                features["is_metro_area"] = 0
                return features

            state, city = row

            # Metro area indicator (simplified - major cities)
            metro_cities = [
                "são paulo", "rio de janeiro", "belo horizonte",
                "brasília", "salvador", "fortaleza", "curitiba",
                "recife", "porto alegre", "manaus"
            ]
            features["is_metro_area"] = 1 if city.lower() in metro_cities else 0

            # State price index (simplified - would use external data)
            # SP = 1.0 (baseline), other states adjusted
            state_multiplier = {
                "SP": 1.0,
                "RJ": 1.05,
                "MG": 0.95,
                "RS": 0.90,
                "PR": 0.92,
                "SC": 0.91,
                "BA": 0.85,
                "PE": 0.87,
                "CE": 0.86,
                "DF": 1.02,
            }
            features["region_price_index"] = state_multiplier.get(state, 0.95)

            # Demand by state (simplified)
            high_demand_states = ["SP", "RJ", "MG", "RS", "PR"]
            features["demand_by_state"] = 1.0 if state in high_demand_states else 0.7

        except Exception:
            features["region_price_index"] = 1.0
            features["demand_by_state"] = 0.5
            features["is_metro_area"] = 0

        return features

    async def _extract_competition_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competition-related features"""
        features = {}

        if not self.db_session:
            # Return default values
            features["competitor_count"] = 0
            features["market_saturation"] = 0.0
            features["is_competitive_market"] = 0
            return features

        brand = data.get("brand", "")
        model = data.get("model", "")
        price = data.get("price", 0)

        # Count similar vehicles (same brand, model, year ±1, price ±20%)
        price_min = price * 0.8 if price > 0 else 0
        price_max = price * 1.2 if price > 0 else 999999999
        year = data.get("model_year", datetime.now().year)

        query = text("""
            SELECT COUNT(*) as count
            FROM vehicles
            WHERE brand = :brand
            AND model = :model
            AND model_year BETWEEN :year_min AND :year_max
            AND price BETWEEN :price_min AND :price_max
            AND status = 'available'
            AND id != :vehicle_id
        """)

        try:
            vehicle_id = data.get("id")
            result = await self.db_session.execute(query, {
                "brand": brand,
                "model": model,
                "year_min": year - 1,
                "year_max": year + 1,
                "price_min": price_min,
                "price_max": price_max,
                "vehicle_id": vehicle_id
            })
            features["competitor_count"] = result.scalar() or 0
        except Exception:
            features["competitor_count"] = 0

        # Market saturation (competitor_count normalized)
        max_competitors = 50
        features["market_saturation"] = min(features["competitor_count"] / max_competitors, 1.0)

        # Competitive market indicator
        features["is_competitive_market"] = 1 if features["competitor_count"] > 10 else 0

        return features

    def get_feature_names(self) -> list:
        """Return list of feature names"""
        return self.feature_names

    def get_feature_importance_groups(self) -> Dict[str, list]:
        """Return feature names grouped by category"""
        return {
            "demand": [
                "search_volume", "view_count", "lead_count",
                "demand_score", "is_high_demand"
            ],
            "supply": [
                "inventory_count", "new_listings_7d", "new_listings_30d",
                "supply_score", "is_low_supply"
            ],
            "seasonality": [
                "month", "quarter", "day_of_week", "is_weekend",
                "is_summer", "is_winter", "is_spring", "is_fall",
                "is_holiday_season", "is_year_end", "is_year_start",
                "is_payday_period"
            ],
            "trends": [
                "price_change_30d", "price_change_90d",
                "price_trend_up", "price_trend_down"
            ],
            "geography": [
                "region_price_index", "demand_by_state", "is_metro_area"
            ],
            "competition": [
                "competitor_count", "market_saturation", "is_competitive_market"
            ]
        }
