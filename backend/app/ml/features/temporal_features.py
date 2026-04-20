"""
Temporal Features - Extracts time-based features
"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
import math


class TemporalFeatures:
    """
    Extracts temporal/time-based features for ML models.

    Features categories:
    - Date: day_of_week, day_of_month, month, quarter, year
    - Seasonality: is_summer, is_winter, is_holiday_season
    - Cycles: days_since_listing, weekend_boost
    - Patterns: payday_effect, month_end_effect
    """

    def __init__(self):
        self.feature_names = []

    def extract(self, vehicle_data: Dict[str, Any], reference_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Extract all temporal features.

        Args:
            vehicle_data: Dictionary with vehicle information
            reference_date: Optional reference date (defaults to now)

        Returns:
            Dictionary with temporal features
        """
        if reference_date is None:
            reference_date = datetime.now()

        features = {}

        # Date features (8)
        features.update(self._extract_date_features(reference_date))

        # Seasonality features (8)
        features.update(self._extract_seasonality_features(reference_date))

        # Cycle features (6)
        features.update(self._extract_cycle_features(vehicle_data, reference_date))

        # Pattern features (5)
        features.update(self._extract_pattern_features(reference_date))

        self.feature_names = list(features.keys())
        return features

    def _extract_date_features(self, ref_date: datetime) -> Dict[str, Any]:
        """Extract basic date features"""
        features = {}

        # Day features
        features["day_of_week"] = ref_date.weekday()  # 0=Monday, 6=Sunday
        features["day_of_month"] = ref_date.day
        features["day_of_year"] = ref_date.timetuple().tm_yday

        # Week of month (1-5)
        features["week_of_month"] = (ref_date.day - 1) // 7 + 1

        # Month features
        features["month"] = ref_date.month
        features["quarter"] = (ref_date.month - 1) // 3 + 1
        features["year"] = ref_date.year

        # Is month start/end
        features["is_month_start"] = 1 if ref_date.day <= 5 else 0
        features["is_month_end"] = 1 if ref_date.day >= 25 else 0

        return features

    def _extract_seasonality_features(self, ref_date: datetime) -> Dict[str, Any]:
        """Extract seasonality features"""
        features = {}

        month = ref_date.month

        # Seasons (Southern Hemisphere / Brazil)
        features["is_summer"] = 1 if month in [12, 1, 2] else 0
        features["is_winter"] = 1 if month in [6, 7, 8] else 0
        features["is_spring"] = 1 if month in [9, 10, 11] else 0
        features["is_fall"] = 1 if month in [3, 4, 5] else 0

        # Holiday seasons (Brazil)
        # Christmas/New Year (Dec-Jan)
        features["is_christmas_season"] = 1 if month == 12 or (month == 1 and ref_date.day <= 7) else 0

        # Carnival (Feb-Mar, varies)
        features["is_carnival_season"] = 1 if month in [2, 3] else 0

        # Easter (Mar-Apr, varies)
        features["is_easter_season"] = 1 if month in [3, 4] else 0

        # School holidays (Jan-Feb, Jul)
        features["is_school_holiday"] = 1 if month in [1, 2, 7] else 0

        # Vacation months (Dec, Jan, Jul)
        features["is_vacation_month"] = 1 if month in [12, 1, 7] else 0

        # Tax season (May - when people get tax refunds)
        features["is_tax_season"] = 1 if month == 5 else 0

        # Year-end bonus season (Nov-Dec)
        features["is_bonus_season"] = 1 if month in [11, 12] else 0

        return features

    def _extract_cycle_features(self, vehicle_data: Dict[str, Any], ref_date: datetime) -> Dict[str, Any]:
        """Extract cycle-related features"""
        features = {}

        # Weekend boost
        features["is_weekend"] = 1 if ref_date.weekday() >= 5 else 0
        features["is_friday"] = 1 if ref_date.weekday() == 4 else 0

        # Days since listing
        created_at = vehicle_data.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            elif not isinstance(created_at, datetime):
                created_at = datetime.combine(created_at, datetime.min.time())

            days_since = (ref_date - created_at).days
            features["days_since_listing"] = max(0, days_since)
            features["weeks_since_listing"] = max(0, days_since // 7)
            features["months_since_listing"] = max(0, days_since // 30)

            # Listing age buckets
            features["is_fresh_listing"] = 1 if days_since < 7 else 0
            features["is_recent_listing"] = 1 if 7 <= days_since < 30 else 0
            features["is_stale_listing"] = 1 if days_since >= 90 else 0
        else:
            features["days_since_listing"] = 0
            features["weeks_since_listing"] = 0
            features["months_since_listing"] = 0
            features["is_fresh_listing"] = 0
            features["is_recent_listing"] = 0
            features["is_stale_listing"] = 0

        return features

    def _extract_pattern_features(self, ref_date: datetime) -> Dict[str, Any]:
        """Extract pattern-based features"""
        features = {}

        day = ref_date.day
        weekday = ref_date.weekday()

        # Payday effect (1st-5th and 25th-31st are typical paydays)
        features["is_payday_period"] = 1 if day <= 5 or day >= 25 else 0
        features["is_early_payday"] = 1 if day <= 5 else 0
        features["is_late_payday"] = 1 if day >= 25 else 0

        # 15th also a common payday (mid-month)
        features["is_mid_month_payday"] = 1 if 14 <= day <= 16 else 0

        # Week start/end effects
        features["is_week_start"] = 1 if weekday == 0 else 0  # Monday
        features["is_week_end"] = 1 if weekday == 4 else 0  # Friday

        # Start of quarter (business planning)
        quarter_start_months = [1, 4, 7, 10]
        features["is_quarter_start"] = 1 if (ref_date.month in quarter_start_months and ref_date.day <= 7) else 0

        # End of quarter (sales targets)
        quarter_end_months = [3, 6, 9, 12]
        features["is_quarter_end"] = 1 if (ref_date.month in quarter_end_months and ref_date.day >= 25) else 0

        return features

    def get_feature_names(self) -> list:
        """Return list of feature names"""
        return self.feature_names

    def get_feature_importance_groups(self) -> Dict[str, list]:
        """Return feature names grouped by category"""
        return {
            "date": [
                "day_of_week", "day_of_month", "day_of_year", "week_of_month",
                "month", "quarter", "year", "is_month_start", "is_month_end"
            ],
            "seasonality": [
                "is_summer", "is_winter", "is_spring", "is_fall",
                "is_christmas_season", "is_carnival_season", "is_easter_season",
                "is_school_holiday", "is_vacation_month", "is_tax_season", "is_bonus_season"
            ],
            "cycles": [
                "is_weekend", "is_friday",
                "days_since_listing", "weeks_since_listing", "months_since_listing",
                "is_fresh_listing", "is_recent_listing", "is_stale_listing"
            ],
            "patterns": [
                "is_payday_period", "is_early_payday", "is_late_payday",
                "is_mid_month_payday", "is_week_start", "is_week_end",
                "is_quarter_start", "is_quarter_end"
            ]
        }
