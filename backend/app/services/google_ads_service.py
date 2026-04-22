"""
Google Ads Publisher Service.
"""
import logging
from typing import Dict, Any, Optional
from uuid import UUID

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2.credentials import Credentials

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.google_account import GoogleAccount
from app.schemas.google import GooglePublishResponse


logger = logging.getLogger(__name__)


class GoogleAdsPublisher:
    """Service for publishing ads to Google Ads platform."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def publish_ad(
        self,
        ad_id: UUID,
        google_customer_id: str,
        campaign_name: str,
        ad_group_name: str,
        budget_amount: float,
        status: str = "PAUSED"
    ) -> GooglePublishResponse:
        """
        Publish an ad to Google Ads.

        Args:
            ad_id: Internal ad ID
            google_customer_id: Google Ads Customer ID
            campaign_name: Campaign name
            ad_group_name: Ad group name
            budget_amount: Daily budget amount
            status: Initial ad status

        Returns:
            GooglePublishResponse with created IDs
        """
        try:
            # Get internal ad
            result = await self.db.execute(
                select(Ad).where(Ad.id == ad_id)
            )
            internal_ad = result.scalar_one_or_none()

            if not internal_ad:
                return GooglePublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message="Ad not found",
                    errors=["Ad not found in database"]
                )

            # Get Google account credentials
            result = await self.db.execute(
                select(GoogleAccount).where(
                    GoogleAccount.google_account_id == google_customer_id
                )
            )
            google_account = result.scalar_one_or_none()

            if not google_account:
                return GooglePublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message="Google Ads account not connected",
                    errors=["Google Ads account not found in database"]
                )

            # Create Google Ads client
            credentials = Credentials(
                token=google_account.access_token,
                refresh_token=google_account.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=google_account.access_token,  # These should be from config
                client_secret=google_account.refresh_token
            )

            # Note: In production, you should get these from settings
            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=google_account.access_token  # Should be from config
            )

            # Step 1: Create Campaign
            campaign_response = await self._create_campaign(
                client=client,
                customer_id=google_customer_id,
                name=campaign_name,
                budget_amount=budget_amount,
                status=status
            )

            if not campaign_response["success"]:
                return GooglePublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message=f"Failed to create campaign: {campaign_response['message']}",
                    errors=campaign_response.get("errors", [])
                )

            google_campaign_id = campaign_response["campaign_id"]
            logger.info(f"Created Google campaign: {google_campaign_id}")

            # Step 2: Create Ad Group
            adgroup_response = await self._create_ad_group(
                client=client,
                customer_id=google_customer_id,
                campaign_id=google_campaign_id,
                name=ad_group_name,
                status=status
            )

            if not adgroup_response["success"]:
                return GooglePublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message=f"Failed to create ad group: {adgroup_response['message']}",
                    errors=adgroup_response.get("errors", [])
                )

            google_adgroup_id = adgroup_response["adgroup_id"]
            logger.info(f"Created Google ad group: {google_adgroup_id}")

            # Step 3: Create Ad
            ad_response = await self._create_ad(
                client=client,
                customer_id=google_customer_id,
                adgroup_id=google_adgroup_id,
                ad_data=internal_ad,
                status=status
            )

            if not ad_response["success"]:
                return GooglePublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message=f"Failed to create ad: {ad_response['message']}",
                    errors=ad_response.get("errors", [])
                )

            google_ad_id = ad_response["ad_id"]
            logger.info(f"Created Google ad: {google_ad_id}")

            # Update internal ad with Google IDs
            internal_ad.platform_ad_id = google_ad_id
            internal_ad.status = "active" if status == "ENABLED" else "scheduled"
            await self.db.commit()

            return GooglePublishResponse(
                success=True,
                ad_id=ad_id,
                google_campaign_id=google_campaign_id,
                google_adgroup_id=google_adgroup_id,
                google_ad_id=google_ad_id,
                message="Ad published successfully to Google Ads"
            )

        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex.error.message()}")
            return GooglePublishResponse(
                success=False,
                ad_id=ad_id,
                message=f"Google Ads API error: {ex.error.message()}",
                errors=[str(ex)]
            )
        except Exception as e:
            logger.error(f"Error publishing ad: {str(e)}")
            return GooglePublishResponse(
                success=False,
                ad_id=ad_id,
                message=f"Unexpected error: {str(e)}",
                errors=[str(e)]
            )

    async def _create_campaign(
        self,
        client: GoogleAdsClient,
        customer_id: str,
        name: str,
        budget_amount: float,
        status: str
    ) -> Dict[str, Any]:
        """Create Google Ads campaign."""
        try:
            campaign_service = client.get_service("CampaignService")
            budget_service = client.get_service("CampaignBudgetService")

            # Create budget
            budget_operation = client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            budget.name = f"{name} - Budget"
            budget.amount_micros = int(budget_amount * 1_000_000)  # Convert to micros
            budget.delivery_method = client.get_type("BudgetDeliveryMethodEnum").STANDARD

            # Add budget
            budget_response = budget_service.mutate_campaign_budget(
                customer_id=customer_id,
                operations=[budget_operation]
            )

            budget_id = budget_response.results[0].resource_name

            # Create campaign
            campaign_operation = client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = name
            campaign.campaign_budget = budget_id
            campaign.advertising_channel_type = client.get_type("AdvertisingChannelTypeEnum").SEARCH
            campaign.status = self._map_status(status)
            campaign.manual_cpc.enhanced_cpc_enabled = True

            # Add campaign
            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )

            campaign_id = campaign_response.results[0].resource_name.split("/")[-1]

            return {
                "success": True,
                "campaign_id": campaign_id
            }

        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    async def _create_ad_group(
        self,
        client: GoogleAdsClient,
        customer_id: str,
        campaign_id: str,
        name: str,
        status: str
    ) -> Dict[str, Any]:
        """Create Google Ads ad group."""
        try:
            adgroup_service = client.get_service("AdGroupService")

            # Create ad group
            adgroup_operation = client.get_type("AdGroupOperation")
            adgroup = adgroup_operation.create
            adgroup.name = name
            adgroup.status = self._map_status(status)
            adgroup.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
            adgroup.type_ = client.get_type("AdGroupTypeEnum").SEARCH_STANDARD
            adgroup.cpc_bid_micros = 1_000_000  # $1.00 default bid

            # Add ad group
            adgroup_response = adgroup_service.mutate_ad_groups(
                customer_id=customer_id,
                operations=[adgroup_operation]
            )

            adgroup_id = adgroup_response.results[0].resource_name.split("/")[-1]

            return {
                "success": True,
                "adgroup_id": adgroup_id
            }

        except Exception as e:
            logger.error(f"Error creating ad group: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    async def _create_ad(
        self,
        client: GoogleAdsClient,
        customer_id: str,
        adgroup_id: str,
        ad_data: Ad,
        status: str
    ) -> Dict[str, Any]:
        """Create Google Ads expanded text ad."""
        try:
            adgroup_ad_service = client.get_service("AdGroupAdService")

            # Create expanded text ad
            ad_operation = client.get_type("AdGroupAdOperation")
            adgroup_ad = ad_operation.create
            adgroup_ad.status = self._map_status(status)
            adgroup_ad.ad_group = f"customers/{customer_id}/adGroups/{adgroup_id}"

            # Create expanded text ad
            expanded_text_ad = client.get_type("ExpandedTextAdInfo")
            expanded_text_ad.headline_part1 = self._truncate_text(ad_data.headline or ad_data.title, 30)
            expanded_text_ad.headline_part2 = self._truncate_text(ad_data.description or "", 30)
            expanded_text_ad.description = self._truncate_text(ad_data.description or "", 90)

            # Add final URL
            if ad_data.images:
                expanded_text_ad.final_urls.append(ad_data.images[0])  # Use first image as URL
            else:
                expanded_text_ad.final_urls.append("https://example.com")  # TODO: Use vehicle landing page

            adgroup_ad.ad.expanded_text_ad = expanded_text_ad

            # Add ad
            ad_response = adgroup_ad_service.mutate_ad_group_ads(
                customer_id=customer_id,
                operations=[ad_operation]
            )

            ad_id = ad_response.results[0].resource_name.split("/")[-1]

            return {
                "success": True,
                "ad_id": ad_id
            }

        except Exception as e:
            logger.error(f"Error creating ad: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def _map_status(self, status: str) -> Any:
        """Map internal status to Google Ads status."""
        # This should be done with proper client enums
        # Simplified for now
        status_map = {
            "ENABLED": 2,  # ENABLED
            "PAUSED": 3,   # PAUSED
            "REMOVED": 4   # REMOVED
        }
        return status_map.get(status.upper(), 3)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length."""
        if not text:
            return ""
        return text[:max_length] if len(text) > max_length else text
