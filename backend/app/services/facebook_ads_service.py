"""
Facebook Ads Publisher Service.
"""
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adimage import AdImage
from facebook_business.exceptions import FacebookRequestError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.facebook_account import FacebookAccount
from app.models.vehicle import Vehicle
from app.schemas.facebook import FacebookPublishResponse


logger = logging.getLogger(__name__)


class FacebookAdsPublisher:
    """Service for publishing ads to Facebook Ads platform."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def publish_ad(
        self,
        ad_id: UUID,
        facebook_account_id: str,
        campaign_name: str,
        adset_name: str,
        objective: str = "OUTCOME_TRAFFIC",
        status: str = "PAUSED"
    ) -> FacebookPublishResponse:
        """
        Publish an ad to Facebook Ads.

        Args:
            ad_id: Internal ad ID
            facebook_account_id: Facebook Ad Account ID
            campaign_name: Campaign name
            adset_name: Ad set name
            objective: Campaign objective
            status: Initial ad status

        Returns:
            FacebookPublishResponse with created IDs
        """
        try:
            # Get internal ad
            result = await self.db.execute(
                select(Ad).where(Ad.id == ad_id)
            )
            internal_ad = result.scalar_one_or_none()

            if not internal_ad:
                return FacebookPublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message="Ad not found",
                    errors=["Ad not found in database"]
                )

            # Get Facebook account credentials
            result = await self.db.execute(
                select(FacebookAccount).where(
                    FacebookAccount.facebook_account_id == facebook_account_id
                )
            )
            fb_account = result.scalar_one_or_none()

            if not fb_account:
                return FacebookPublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message="Facebook account not connected",
                    errors=["Facebook account not found in database"]
                )

            # Initialize Facebook Ads API
            FacebookAdsApi.init(
                app_id=fb_account.access_token,
                access_token=fb_account.access_token
            )

            # Get Facebook Ad Account
            account = AdAccount(fb_account_id)

            # Step 1: Create Campaign
            campaign = self._create_campaign(
                account=account,
                name=campaign_name,
                objective=objective,
                status=status
            )

            if not campaign:
                return FacebookPublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message="Failed to create campaign",
                    errors=["Campaign creation failed"]
                )

            logger.info(f"Created Facebook campaign: {campaign['id']}")

            # Step 2: Create Ad Set
            adset = self._create_adset(
                account=account,
                campaign_id=campaign["id"],
                name=adset_name,
                daily_budget=str(internal_ad.budget_daily) if internal_ad.budget_daily else "100",
                start_time=internal_ad.start_date,
                end_time=internal_ad.end_date,
                targeting=internal_ad.target_audience,
                status=status
            )

            if not adset:
                return FacebookPublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message="Failed to create ad set",
                    errors=["Ad set creation failed"]
                )

            logger.info(f"Created Facebook ad set: {adset['id']}")

            # Step 3: Upload images and get hashes
            image_hashes = []
            if internal_ad.images:
                image_hashes = await self._upload_images(
                    account=account,
                    image_urls=internal_ad.images
                )

            # Step 4: Create Creative
            creative = self._create_creative(
                account=account,
                ad_data=internal_ad,
                image_hashes=image_hashes
            )

            if not creative:
                return FacebookPublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message="Failed to create creative",
                    errors=["Creative creation failed"]
                )

            logger.info(f"Created Facebook creative: {creative['id']}")

            # Step 5: Create Ad
            facebook_ad = self._create_ad(
                account=account,
                adset_id=adset["id"],
                creative_id=creative["id"],
                name=internal_ad.title,
                status=status
            )

            if not facebook_ad:
                return FacebookPublishResponse(
                    success=False,
                    ad_id=ad_id,
                    message="Failed to create ad",
                    errors=["Ad creation failed"]
                )

            logger.info(f"Created Facebook ad: {facebook_ad['id']}")

            # Update internal ad with Facebook IDs
            internal_ad.platform_ad_id = facebook_ad["id"]
            internal_ad.status = "active" if status == "ACTIVE" else "scheduled"
            await self.db.commit()

            return FacebookPublishResponse(
                success=True,
                ad_id=ad_id,
                facebook_campaign_id=campaign["id"],
                facebook_adset_id=adset["id"],
                facebook_ad_id=facebook_ad["id"],
                message="Ad published successfully to Facebook"
            )

        except FacebookRequestError as e:
            logger.error(f"Facebook API error: {e.api_error_message()}")
            return FacebookPublishResponse(
                success=False,
                ad_id=ad_id,
                message=f"Facebook API error: {e.api_error_message()}",
                errors=[str(e)]
            )
        except Exception as e:
            logger.error(f"Error publishing ad: {str(e)}")
            return FacebookPublishResponse(
                success=False,
                ad_id=ad_id,
                message=f"Unexpected error: {str(e)}",
                errors=[str(e)]
            )

    def _create_campaign(
        self,
        account: AdAccount,
        name: str,
        objective: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """Create Facebook campaign."""
        try:
            params = {
                Campaign.Field.name: name,
                Campaign.Field.objective: objective,
                Campaign.Field.status: status,
                Campaign.Field.special_ad_categories: [],
            }

            campaign = account.create_campaign(params=params)

            return {"id": campaign["id"]}

        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return None

    def _create_adset(
        self,
        account: AdAccount,
        campaign_id: str,
        name: str,
        daily_budget: str,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
        targeting: Optional[Dict[str, Any]] = None,
        status: str = "PAUSED"
    ) -> Optional[Dict[str, Any]]:
        """Create Facebook ad set."""
        try:
            # Build targeting spec
            targeting_spec = self._build_targeting_spec(targeting)

            params = {
                AdSet.Field.name: name,
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.daily_budget: daily_budget,
                AdSet.Field.targeting: targeting_spec,
                AdSet.Field.status: status,
                AdSet.Field.optimization_goal: "TRAFFIC",
                AdSet.Field.billing_event: "IMPRESSIONS",
            }

            # Add optional dates
            if start_time:
                params[AdSet.Field.start_time] = start_time.isoformat()
            if end_time:
                params[AdSet.Field.end_time] = end_time.isoformat()

            adset = account.create_ad_set(params=params)

            return {"id": adset["id"]}

        except Exception as e:
            logger.error(f"Error creating ad set: {str(e)}")
            return None

    def _build_targeting_spec(
        self,
        targeting: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build Facebook targeting spec from internal targeting."""
        if not targeting:
            # Default targeting for Brazil
            return {
                "geo_locations": {
                    "countries": ["BR"]
                },
                "age_min": 25,
                "age_max": 55,
            }

        spec = {}

        # Locations
        if "locations" in targeting:
            geo_locations = {"countries": []}
            for location in targeting["locations"]:
                if "city" in location:
                    geo_locations.setdefault("cities", []).append({
                        "name": location["city"],
                        "radius": location.get("radius", 30),
                        "distance_unit": "kilometer"
                    })
                elif "country" in location:
                    geo_locations["countries"].append(location["country"])

            spec["geo_locations"] = geo_locations

        # Age
        if "age_min" in targeting:
            spec["age_min"] = targeting["age_min"]
        if "age_max" in targeting:
            spec["age_max"] = targeting["age_max"]

        # Gender
        if "genders" in targeting:
            genders_map = {"male": 1, "female": 2}
            spec["genders"] = [
                genders_map[g] for g in targeting["genders"] if g in genders_map
            ]

        # Interests
        if "interests" in targeting:
            spec["flexible_spec"] = [{
                "interests": [
                    {"name": interest, "id": str(hash(interest))}
                    for interest in targeting["interests"]
                ]
            }]

        return spec

    async def _upload_images(
        self,
        account: AdAccount,
        image_urls: List[str]
    ) -> List[str]:
        """Upload images to Facebook and return hashes."""
        image_hashes = []

        try:
            for image_url in image_urls:
                # In production, you'd download and upload the actual image
                # For now, we'll use the URL directly
                image = AdImage(parent=account)
                image[AdImage.Field.url] = image_url
                image.remote_create()

                image_hashes.append(image["hash"])

        except Exception as e:
            logger.error(f"Error uploading images: {str(e)}")

        return image_hashes

    def _create_creative(
        self,
        account: AdAccount,
        ad_data: Ad,
        image_hashes: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Create Facebook ad creative."""
        try:
            object_story_spec = {
                "page_id": "",  # TODO: Get from Facebook page connection
            }

            # Add images if available
            if image_hashes:
                object_story_spec["link_data"] = {
                    "image_hash": image_hashes[0],
                    "link": "https://example.com",  # TODO: Use vehicle landing page
                    "message": ad_data.description or ad_data.title,
                    "name": ad_data.headline or ad_data.title,
                    "call_to_action": {
                        "type": self._map_cta(ad_data.call_to_action)
                    }
                }
            else:
                object_story_spec["link_data"] = {
                    "link": "https://example.com",
                    "message": ad_data.description or ad_data.title,
                    "name": ad_data.headline or ad_data.title,
                }

            params = {
                AdCreative.Field.object_story_spec: object_story_spec,
            }

            creative = AdCreative(parent=account).create(params=params)

            return {"id": creative["id"]}

        except Exception as e:
            logger.error(f"Error creating creative: {str(e)}")
            return None

    def _create_ad(
        self,
        account: AdAccount,
        adset_id: str,
        creative_id: str,
        name: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """Create Facebook ad."""
        try:
            params = {
                Ad.Field.name: name,
                Ad.Field.adset_id: adset_id,
                Ad.Field.creative: {"creative_id": creative_id},
                Ad.Field.status: status,
            }

            ad = account.create_ad(params=params)

            return {"id": ad["id"]}

        except Exception as e:
            logger.error(f"Error creating ad: {str(e)}")
            return None

    def _map_cta(self, cta: Optional[str]) -> str:
        """Map internal CTA to Facebook CTA type."""
        cta_map = {
            "Agendar Test-Drive": "GET_DIRECTIONS",
            "Saber Mais": "LEARN_MORE",
            "Contatar": "CONTACT_US",
            "Ver Disponibilidade": "GET_QUOTE",
            "Visitar Site": "OPEN_LINK",
        }

        return cta_map.get(cta, "LEARN_MORE")
