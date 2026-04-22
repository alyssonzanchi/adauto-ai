"""
Facebook Metrics Sync Service.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad as FacebookAd
from facebook_business.adobjects.adinsights import AdInsights
from facebook_business.exceptions import FacebookRequestError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.facebook_account import FacebookAccount
from app.models.ad_metric import AdMetric


logger = logging.getLogger(__name__)


class FacebookMetricsSync:
    """Service for syncing metrics from Facebook Ads."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_account_metrics(
        self,
        facebook_account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ad_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Sync metrics for all ads in a Facebook ad account.

        Args:
            facebook_account_id: Facebook Ad Account ID
            start_date: Start date for metrics (default: 7 days ago)
            end_date: End date for metrics (default: today)
            ad_ids: Specific ad IDs to sync (optional)

        Returns:
            Summary of sync operation
        """
        try:
            # Get Facebook account credentials
            result = await self.db.execute(
                select(FacebookAccount).where(
                    FacebookAccount.facebook_account_id == facebook_account_id
                )
            )
            fb_account = result.scalar_one_or_none()

            if not fb_account:
                raise ValueError(f"Facebook account {facebook_account_id} not found")

            # Initialize Facebook Ads API
            FacebookAdsApi.init(access_token=fb_account.access_token)

            # Set default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()

            # Get Ad Account
            account = AdAccount(facebook_account_id)

            # Get insights for the account
            ads_synced = 0
            errors = []

            # Build insights query parameters
            params = {
                "date_preset": "lifetime" if not start_date else "custom",
                "time_range": {
                    "since": start_date.strftime("%Y-%m-%d"),
                    "until": end_date.strftime("%Y-%m-%d")
                } if start_date else None,
                "level": "ad",
                "fields": [
                    AdInsights.Field.ad_id,
                    AdInsights.Field.impressions,
                    AdInsights.Field.clicks,
                    AdInsights.Field.spend,
                    AdInsights.Field.actions,
                    AdInsights.Field.action_values,
                    AdInsights.Field.conversions,
                    AdInsights.Field.cost_per_conversion,
                    AdInsights.Field.frequency,
                    AdInsights.Field.reach,
                    AdInsights.Field.ctr,
                    AdInsights.Field.cpc,
                    AdInsights.Field.cpp,
                    AdInsights.Field.date_start,
                    AdInsights.Field.date_stop,
                ],
            }

            if not start_date:
                params.pop("time_range", None)

            # Get insights
            insights = account.get_insights(**params)

            async for insight in insights:
                try:
                    await self._process_insight(insight, fb_account.dealership_id)
                    ads_synced += 1
                except Exception as e:
                    logger.error(f"Error processing insight: {str(e)}")
                    errors.append(str(e))

            # Update last_synced_at
            fb_account.last_synced_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"Synced {ads_synced} ads from Facebook account {facebook_account_id}")

            return {
                "success": True,
                "account_id": facebook_account_id,
                "ads_updated": ads_synced,
                "period_start": start_date,
                "period_end": end_date,
                "errors": errors,
                "message": f"Successfully synced {ads_synced} ads"
            }

        except Exception as e:
            logger.error(f"Error syncing metrics: {str(e)}")
            raise

    async def sync_single_ad_metrics(
        self,
        internal_ad_id: UUID,
        facebook_account_id: str
    ) -> Dict[str, Any]:
        """
        Sync metrics for a single ad.

        Args:
            internal_ad_id: Internal ad ID
            facebook_account_id: Facebook Ad Account ID

        Returns:
            Sync result
        """
        try:
            # Get internal ad
            result = await self.db.execute(
                select(Ad).where(Ad.id == internal_ad_id)
            )
            internal_ad = result.scalar_one_or_none()

            if not internal_ad or not internal_ad.platform_ad_id:
                raise ValueError(f"Ad {internal_ad_id} not found or not published to Facebook")

            # Get Facebook account
            result = await self.db.execute(
                select(FacebookAccount).where(
                    FacebookAccount.facebook_account_id == facebook_account_id
                )
            )
            fb_account = result.scalar_one_or_none()

            if not fb_account:
                raise ValueError(f"Facebook account {facebook_account_id} not found")

            # Initialize API
            FacebookAdsApi.init(access_token=fb_account.access_token)

            # Get insights for specific ad
            account = AdAccount(facebook_account_id)

            params = {
                "date_preset": "maximum",  # All time
                "level": "ad",
                "filtering": [{
                    "field": "ad.id",
                    "operator": "IN",
                    "value": [internal_ad.platform_ad_id]
                }],
                "fields": [
                    AdInsights.Field.impressions,
                    AdInsights.Field.clicks,
                    AdInsights.Field.spend,
                    AdInsights.Field.actions,
                    AdInsights.Field.conversions,
                    AdInsights.Field.ctr,
                    AdInsights.Field.cpc,
                ],
            }

            insights = account.get_insights(**params)

            ads_synced = 0
            async for insight in insights:
                await self._process_insight(insight, fb_account.dealership_id, internal_ad_id)
                ads_synced += 1

            logger.info(f"Synced metrics for ad {internal_ad_id}")

            return {
                "success": True,
                "ad_id": str(internal_ad_id),
                "ads_updated": ads_synced,
                "message": "Successfully synced ad metrics"
            }

        except Exception as e:
            logger.error(f"Error syncing ad metrics: {str(e)}")
            raise

    async def _process_insight(
        self,
        insight: Any,
        dealership_id: UUID,
        internal_ad_id: Optional[UUID] = None
    ):
        """Process Facebook insight and create/update AdMetric record."""
        try:
            facebook_ad_id = insight.get(AdInsights.Field.ad_id)

            # Get internal ad if not provided
            if not internal_ad_id:
                result = await self.db.execute(
                    select(Ad).where(
                        Ad.platform_ad_id == facebook_ad_id,
                        Ad.platform == "facebook"
                    )
                )
                internal_ad = result.scalar_one_or_none()

                if not internal_ad:
                    logger.warning(f"Internal ad not found for Facebook ad {facebook_ad_id}")
                    return

                internal_ad_id = internal_ad.id
                internal_ad = internal_ad
            else:
                internal_ad = insight  # Placeholder

            # Extract metrics
            impressions = int(insight.get(AdInsights.Field.impressions, 0))
            clicks = int(insight.get(AdInsights.Field.clicks, 0))
            spend = float(insight.get(AdInsights.Field.spend, 0))

            # Extract conversions
            conversions = 0
            actions = insight.get(AdInsights.Field.actions, [])
            if actions:
                for action in actions:
                    if action.get("action_type") == "offsite_conversion":
                        conversions += int(action.get("value", 0))

            # Calculate metrics
            ctr = float(insight.get(AdInsights.Field.ctr, 0)) or (
                (clicks / impressions * 100) if impressions > 0 else 0
            )
            cpc = float(insight.get(AdInsights.Field.cpc, 0)) or (
                (spend / clicks) if clicks > 0 else 0
            )

            # Get date range
            date_start = datetime.strptime(
                insight.get(AdInsights.Field.date_start),
                "%Y-%m-%d"
            )
            date_stop = datetime.strptime(
                insight.get(AdInsights.Field.date_stop),
                "%Y-%m-%d"
            )

            # Check if metric already exists
            from sqlalchemy import and_
            result = await self.db.execute(
                select(AdMetric).where(
                    and_(
                        AdMetric.ad_id == internal_ad_id,
                        AdMetric.date == date_start.date()
                    )
                )
            )
            existing_metric = result.scalar_one_or_none()

            if existing_metric:
                # Update existing metric
                existing_metric.impressions = impressions
                existing_metric.clicks = clicks
                existing_metric.spend = spend
                existing_metric.conversions = conversions
                existing_metric.ctr = ctr
                existing_metric.cpc = cpc
            else:
                # Create new metric
                metric = AdMetric(
                    ad_id=internal_ad_id,
                    date=date_start.date(),
                    impressions=impressions,
                    clicks=clicks,
                    spend=spend,
                    conversions=conversions,
                    ctr=ctr,
                    cpc=cpc,
                )
                self.db.add(metric)

            await self.db.commit()

        except Exception as e:
            logger.error(f"Error processing insight: {str(e)}")
            raise

    async def get_realtime_metrics(
        self,
        internal_ad_id: UUID,
        facebook_account_id: str
    ) -> Dict[str, Any]:
        """
        Get real-time metrics for an ad.

        Args:
            internal_ad_id: Internal ad ID
            facebook_account_id: Facebook Ad Account ID

        Returns:
            Real-time metrics
        """
        try:
            # Get internal ad
            result = await self.db.execute(
                select(Ad).where(Ad.id == internal_ad_id)
            )
            internal_ad = result.scalar_one_or_none()

            if not internal_ad or not internal_ad.platform_ad_id:
                raise ValueError("Ad not found or not published")

            # Get Facebook account
            result = await self.db.execute(
                select(FacebookAccount).where(
                    FacebookAccount.facebook_account_id == facebook_account_id
                )
            )
            fb_account = result.scalar_one_or_none()

            if not fb_account:
                raise ValueError("Facebook account not found")

            # Initialize API
            FacebookAdsApi.init(access_token=fb_account.access_token)

            # Get ad
            ad = FacebookAd(internal_ad.platform_ad_id)

            # Get insights (today only)
            insights = ad.get_insights(
                date_preset="today",
                fields=[
                    AdInsights.Field.impressions,
                    AdInsights.Field.clicks,
                    AdInsights.Field.spend,
                    AdInsights.Field.ctr,
                ]
            )

            insights_list = list(insights)

            if not insights_list:
                return {
                    "ad_id": str(internal_ad_id),
                    "impressions": 0,
                    "clicks": 0,
                    "spend": 0,
                    "ctr": 0,
                }

            insight = insights_list[0]

            return {
                "ad_id": str(internal_ad_id),
                "impressions": int(insight.get(AdInsights.Field.impressions, 0)),
                "clicks": int(insight.get(AdInsights.Field.clicks, 0)),
                "spend": float(insight.get(AdInsights.Field.spend, 0)),
                "ctr": float(insight.get(AdInsights.Field.ctr, 0)),
            }

        except Exception as e:
            logger.error(f"Error getting real-time metrics: {str(e)}")
            raise
