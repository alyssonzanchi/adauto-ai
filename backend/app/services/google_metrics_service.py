"""
Google Ads Metrics Sync Service.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from uuid import UUID

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2.credentials import Credentials

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.google_account import GoogleAccount
from app.models.ad_metric import AdMetric


logger = logging.getLogger(__name__)


class GoogleMetricsSync:
    """Service for syncing metrics from Google Ads."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_account_metrics(
        self,
        google_customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ad_ids: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Sync metrics for all ads in a Google Ads account.

        Args:
            google_customer_id: Google Ads Customer ID
            start_date: Start date for metrics (default: 7 days ago)
            end_date: End date for metrics (default: today)
            ad_ids: Specific ad IDs to sync (optional)

        Returns:
            Summary of sync operation
        """
        try:
            # Get Google account credentials
            result = await self.db.execute(
                select(GoogleAccount).where(
                    GoogleAccount.google_account_id == google_customer_id
                )
            )
            google_account = result.scalar_one_or_none()

            if not google_account:
                raise ValueError(f"Google Ads account {google_customer_id} not found")

            # Create Google Ads client
            credentials = Credentials(
                token=google_account.access_token,
                refresh_token=google_account.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=google_account.access_token,
                client_secret=google_account.refresh_token
            )

            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=google_account.access_token
            )

            # Set default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()

            # Get Google Ads Service
            google_ads_service = client.get_service("GoogleAdsService")

            # Build GAQL query for metrics
            query = f"""
                SELECT
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.name,
                    ad_group_ad.campaign,
                    ad_group_ad.ad_group,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.cost_per_conversion
                FROM ad_group_ad
                WHERE segments.date BETWEEN '{start_date.strftime("%Y-%m-%d")}' AND '{end_date.strftime("%Y-%m-%d")}'
            """

            # Create request
            request = client.get_type("SearchGoogleAdsStreamRequest")
            request.customer_id = google_customer_id
            request.query = query

            # Execute query
            response = google_ads_service.search_stream(request=request)

            ads_synced = 0
            errors = []

            # Process results
            async for batch in response:
                for row in batch:
                    try:
                        await self._process_metrics_row(row, google_account.dealership_id)
                        ads_synced += 1
                    except Exception as e:
                        logger.error(f"Error processing metrics row: {str(e)}")
                        errors.append(str(e))

            # Update last_synced_at
            google_account.last_synced_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"Synced {ads_synced} ads from Google Ads account {google_customer_id}")

            return {
                "success": True,
                "customer_id": google_customer_id,
                "ads_updated": ads_synced,
                "period_start": start_date,
                "period_end": end_date,
                "errors": errors,
                "message": f"Successfully synced {ads_synced} ads"
            }

        except Exception as e:
            logger.error(f"Error syncing metrics: {str(e)}")
            raise

    async def _process_metrics_row(
        self,
        row: Any,
        dealership_id: UUID,
        internal_ad_id: Optional[UUID] = None
    ):
        """Process Google Ads metrics row and create/update AdMetric record."""
        try:
            google_ad_id = row.ad_group_ad.ad.id
            google_ad_name = row.ad_group_ad.ad.name

            # Get internal ad via platform_ad_id
            result = await self.db.execute(
                select(Ad).where(
                    Ad.platform_ad_id == str(google_ad_id),
                    Ad.platform == "google"
                )
            )
            internal_ad = result.scalar_one_or_none()

            if not internal_ad:
                logger.warning(f"Internal ad not found for Google ad {google_ad_id}")
                return

            # Extract metrics
            impressions = row.metrics.impressions if hasattr(row.metrics, 'impressions') else 0
            clicks = row.metrics.clicks if hasattr(row.metrics, 'clicks') else 0
            spend_micros = row.metrics.cost_micros if hasattr(row.metrics, 'cost_micros') else 0
            spend = spend_micros / 1_000_000  # Convert to dollars
            conversions = row.metrics.conversions if hasattr(row.metrics, 'conversions') else 0

            # Calculate metrics
            ctr = row.metrics.ctr if hasattr(row.metrics, 'ctr') else 0
            cpc = (spend / clicks) if clicks > 0 else 0

            # Get date from segments (if available)
            # Note: Stream responses don't have segments.date in the same way
            # For simplicity, we'll use today's date
            date = datetime.utcnow().date()

            # Check if metric already exists
            from sqlalchemy import and_
            result = await self.db.execute(
                select(AdMetric).where(
                    and_(
                        AdMetric.ad_id == internal_ad.id,
                        AdMetric.date == date
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
                existing_metric.ctr = ctr * 100 if ctr < 1 else ctr  # Convert to percentage
                existing_metric.cpc = cpc
            else:
                # Create new metric
                metric = AdMetric(
                    ad_id=internal_ad.id,
                    date=date,
                    impressions=impressions,
                    clicks=clicks,
                    spend=spend,
                    conversions=conversions,
                    ctr=ctr * 100 if ctr < 1 else ctr,
                    cpc=cpc,
                )
                self.db.add(metric)

            await self.db.commit()

        except Exception as e:
            logger.error(f"Error processing metrics row: {str(e)}")
            raise

    async def get_realtime_metrics(
        self,
        internal_ad_id: UUID,
        google_customer_id: str
    ) -> Dict[str, Any]:
        """
        Get real-time metrics for a specific ad.

        Args:
            internal_ad_id: Internal ad ID
            google_customer_id: Google Ads Customer ID

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

            # Get Google account
            result = await self.db.execute(
                select(GoogleAccount).where(
                    GoogleAccount.google_account_id == google_customer_id
                )
            )
            google_account = result.scalar_one_or_none()

            if not google_account:
                raise ValueError("Google Ads account not found")

            # Create client
            credentials = Credentials(
                token=google_account.access_token,
                refresh_token=google_account.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=google_account.access_token,
                client_secret=google_account.refresh_token
            )

            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=google_account.access_token
            )

            # Get service
            google_ads_service = client.get_service("GoogleAdsService")

            # Query for today's metrics
            today = datetime.utcnow().strftime("%Y-%m-%d")
            query = f"""
                SELECT
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.ctr
                FROM ad_group_ad
                WHERE ad_group_ad.ad.id = '{internal_ad.platform_ad_id}'
                AND segments.date = '{today}'
            """

            # Create request
            request = client.get_type("SearchGoogleAdsRequest")
            request.customer_id = google_customer_id
            request.query = query

            # Execute
            response = google_ads_service.search(request=request)

            # Process response
            for row in response:
                return {
                    "ad_id": str(internal_ad_id),
                    "impressions": row.metrics.impressions if hasattr(row.metrics, 'impressions') else 0,
                    "clicks": row.metrics.clicks if hasattr(row.metrics, 'clicks') else 0,
                    "spend": (row.metrics.cost_micros / 1_000_000) if hasattr(row.metrics, 'cost_micros') else 0,
                    "ctr": row.metrics.ctr if hasattr(row.metrics, 'ctr') else 0,
                }

            # No metrics found
            return {
                "ad_id": str(internal_ad_id),
                "impressions": 0,
                "clicks": 0,
                "spend": 0,
                "ctr": 0,
            }

        except Exception as e:
            logger.error(f"Error getting real-time metrics: {str(e)}")
            raise
