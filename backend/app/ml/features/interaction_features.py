"""
Interaction Features - Extracts user interaction features
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class InteractionFeatures:
    """
    Extracts user interaction and engagement features.

    Features categories:
    - Views: view_count, unique_views, view_rate
    - Engagement: avg_session_duration, bounce_rate, click_depth
    - Lead Quality: lead_source, lead_type, engagement_score
    - Device: device_type, os, browser
    """

    def __init__(self):
        self.feature_names = []

    def extract(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all interaction features.

        Args:
            interaction_data: Dictionary with interaction information

        Returns:
            Dictionary with interaction features
        """
        features = {}

        # View features (7)
        features.update(self._extract_view_features(interaction_data))

        # Engagement features (6)
        features.update(self._extract_engagement_features(interaction_data))

        # Lead quality features (5)
        features.update(self._extract_lead_features(interaction_data))

        # Device features (4)
        features.update(self._extract_device_features(interaction_data))

        # Temporal interaction features (3)
        features.update(self._extract_temporal_interaction_features(interaction_data))

        self.feature_names = list(features.keys())
        return features

    def _extract_view_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract view-related features"""
        features = {}

        # View counts
        features["view_count"] = data.get("view_count", 0)
        features["unique_views"] = data.get("unique_views", 0)
        features["repeat_views"] = data.get("repeat_views", 0)

        # View rate (views per day since listing)
        days_since_listing = data.get("days_since_listing", 1)
        if days_since_listing > 0:
            features["view_rate"] = features["view_count"] / days_since_listing
        else:
            features["view_rate"] = 0.0

        # Image views
        features["image_views"] = data.get("image_views", 0)
        features["gallery_views"] = data.get("gallery_views", 0)

        # Phone clicks (lead indicator)
        features["phone_clicks"] = data.get("phone_clicks", 0)

        # View efficiency (unique/total)
        if features["view_count"] > 0:
            features["view_efficiency"] = features["unique_views"] / features["view_count"]
        else:
            features["view_efficiency"] = 0.0

        return features

    def _extract_engagement_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract engagement features"""
        features = {}

        # Session duration (seconds)
        features["avg_session_duration"] = data.get("avg_session_duration", 0)
        features["total_session_duration"] = data.get("total_session_duration", 0)

        # Bounce rate (single page sessions)
        features["bounce_rate"] = data.get("bounce_rate", 0.0)

        # Click depth (pages per session)
        features["avg_click_depth"] = data.get("avg_click_depth", 0)

        # Time on page
        features["avg_time_on_page"] = data.get("avg_time_on_page", 0)

        # Scroll depth (how far users scroll)
        features["avg_scroll_depth"] = data.get("avg_scroll_depth", 0.0)  # 0-1

        # Overall engagement score
        features["engagement_score"] = self._calculate_engagement_score(features)

        return features

    def _extract_lead_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract lead quality features"""
        features = {}

        # Lead source
        lead_source = data.get("lead_source", "unknown").lower()
        features["source_organic"] = 1 if lead_source == "organic" else 0
        features["source_paid"] = 1 if lead_source in ["paid", "ads", "cpc"] else 0
        features["source_social"] = 1 if lead_source in ["social", "facebook", "instagram"] else 0
        features["source_direct"] = 1 if lead_source == "direct" else 0
        features["source_referral"] = 1 if lead_source == "referral" else 0

        # Lead type
        lead_type = data.get("lead_type", "unknown").lower()
        features["is_hot_lead"] = 1 if lead_type == "hot" else 0
        features["is_warm_lead"] = 1 if lead_type == "warm" else 0
        features["is_cold_lead"] = 1 if lead_type == "cold" else 0

        # Lead actions
        features["form_submissions"] = data.get("form_submissions", 0)
        features["test_drive_requests"] = data.get("test_drive_requests", 0)
        features["financing_inquiries"] = data.get("financing_inquiries", 0)

        # Lead quality score
        features["lead_quality_score"] = self._calculate_lead_quality_score(features)

        return features

    def _extract_device_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract device-related features"""
        features = {}

        # Device type
        device_type = data.get("device_type", "desktop").lower()
        features["is_mobile"] = 1 if device_type == "mobile" else 0
        features["is_tablet"] = 1 if device_type == "tablet" else 0
        features["is_desktop"] = 1 if device_type == "desktop" else 0

        # Operating system
        os = data.get("os", "unknown").lower()
        features["os_android"] = 1 if os == "android" else 0
        features["os_ios"] = 1 if os == "ios" else 0
        features["os_windows"] = 1 if os == "windows" else 0
        features["os_macos"] = 1 if os == "macos" else 0

        # Browser (optional)
        browser = data.get("browser", "").lower()
        features["browser_chrome"] = 1 if browser == "chrome" else 0
        features["browser_safari"] = 1 if browser in ["safari", "mobile safari"] else 0
        features["browser_firefox"] = 1 if browser == "firefox" else 0

        return features

    def _extract_temporal_interaction_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal interaction patterns"""
        features = {}

        # Last interaction time
        last_interaction = data.get("last_interaction")
        if last_interaction:
            if isinstance(last_interaction, str):
                last_interaction = datetime.fromisoformat(last_interaction.replace("Z", "+00:00"))
            time_since_last = (datetime.now() - last_interaction).total_seconds() / 3600  # hours
            features["hours_since_last_interaction"] = time_since_last
            features["is_recent_interaction"] = 1 if time_since_last < 24 else 0
        else:
            features["hours_since_last_interaction"] = 9999
            features["is_recent_interaction"] = 0

        # Peak hours
        features["is_business_hours"] = 1 if 9 <= datetime.now().hour < 18 else 0

        # Day of week interaction
        features["is_weekday_interaction"] = 1 if datetime.now().weekday() < 5 else 0

        return features

    def _calculate_engagement_score(self, features: Dict[str, Any]) -> float:
        """Calculate overall engagement score (0-1)"""
        score = 0.0

        # Session duration (up to 5 minutes = good)
        duration_score = min(features["avg_session_duration"] / 300, 1.0)
        score += duration_score * 0.3

        # Scroll depth
        score += features["avg_scroll_depth"] * 0.2

        # Click depth (up to 5 pages)
        click_score = min(features["avg_click_depth"] / 5, 1.0)
        score += click_score * 0.2

        # Low bounce rate (inverse)
        bounce_score = 1 - features["bounce_rate"]
        score += bounce_score * 0.3

        return min(score, 1.0)

    def _calculate_lead_quality_score(self, features: Dict[str, Any]) -> float:
        """Calculate lead quality score (0-100)"""
        score = 0.0

        # Actions
        score += features["form_submissions"] * 20
        score += features["test_drive_requests"] * 30
        score += features["financing_inquiries"] * 25

        # Lead type
        if features["is_hot_lead"]:
            score += 25
        elif features["is_warm_lead"]:
            score += 15
        elif features["is_cold_lead"]:
            score += 5

        return min(score, 100)

    def get_feature_names(self) -> list:
        """Return list of feature names"""
        return self.feature_names

    def get_feature_importance_groups(self) -> Dict[str, list]:
        """Return feature names grouped by category"""
        return {
            "views": [
                "view_count", "unique_views", "repeat_views", "view_rate",
                "image_views", "gallery_views", "phone_clicks", "view_efficiency"
            ],
            "engagement": [
                "avg_session_duration", "total_session_duration", "bounce_rate",
                "avg_click_depth", "avg_time_on_page", "avg_scroll_depth", "engagement_score"
            ],
            "leads": [
                "source_organic", "source_paid", "source_social", "source_direct", "source_referral",
                "is_hot_lead", "is_warm_lead", "is_cold_lead",
                "form_submissions", "test_drive_requests", "financing_inquiries", "lead_quality_score"
            ],
            "device": [
                "is_mobile", "is_tablet", "is_desktop",
                "os_android", "os_ios", "os_windows", "os_macos",
                "browser_chrome", "browser_safari", "browser_firefox"
            ],
            "temporal": [
                "hours_since_last_interaction", "is_recent_interaction",
                "is_business_hours", "is_weekday_interaction"
            ]
        }
