"""
Ad service.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.enums import AdStatus, AdPlatform
from app.models.vehicle import Vehicle
from app.services.ai.orchestrator import get_orchestrator


class AdService:
    """Service for ad operations."""

    def __init__(self):
        """Initialize ad service."""
        self.orchestrator = get_orchestrator()
        self.metrics = {
            "ads_created": 0,
            "ads_updated": 0,
            "ads_published": 0,
            "ads_paused": 0,
            "optimizations_performed": 0,
        }

    async def create_ad(
        self,
        ad_data: Dict[str, Any],
        db: AsyncSession
    ) -> Ad:
        """
        Create new ad with AI suggestions.

        Args:
            ad_data: Ad data dictionary
            db: Database session

        Returns:
            Created ad

        Raises:
            ValueError: If vehicle not found
        """
        ad = Ad(**ad_data)
        ad.status = AdStatus.DRAFT

        # Generate AI suggestions
        vehicle = await self._get_vehicle(ad.vehicle_id, db)
        ad.ai_suggestions = await self._generate_ai_suggestions(vehicle, ad)

        db.add(ad)
        await db.commit()
        await db.refresh(ad)

        self.metrics["ads_created"] += 1
        return ad

    async def update_ad_status(
        self,
        ad_id: UUID,
        new_status: AdStatus,
        reason: Optional[str],
        db: AsyncSession
    ) -> Ad:
        """
        Update ad status with validation.

        Args:
            ad_id: Ad ID
            new_status: New status
            reason: Reason for status change
            db: Database session

        Returns:
            Updated ad

        Raises:
            ValueError: If ad not found or invalid transition
        """
        # Get ad
        ad = await self._get_ad(ad_id, db)

        # Validate status transition
        if not self._is_valid_status_transition(ad.status, new_status):
            raise ValueError(f"Invalid status transition: {ad.status} -> {new_status}")

        # Update status
        ad.status = new_status

        # Set published_at if activating
        if new_status == AdStatus.ACTIVE and not ad.published_at:
            ad.published_at = datetime.utcnow()

        await db.commit()
        await db.refresh(ad)

        status_key = f"ads_{new_status.value}"
        self.metrics[status_key] = self.metrics.get(status_key, 0) + 1

        return ad

    async def optimize_ad(
        self,
        ad_id: UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate optimization suggestions using AI.

        Args:
            ad_id: Ad ID
            db: Database session

        Returns:
            Optimization suggestions

        Raises:
            ValueError: If ad not found
        """
        ad = await self._get_ad(ad_id, db)
        vehicle = await self._get_vehicle(ad.vehicle_id, db)

        # Get current metrics
        ctr = (
            ad.total_clicks / ad.total_impressions
            if ad.total_impressions > 0
            else 0
        )
        conversion_rate = (
            ad.total_conversions / ad.total_clicks
            if ad.total_clicks > 0
            else 0
        )

        current_metrics = {
            "ctr": float(ctr),
            "conversion_rate": float(conversion_rate),
            "impressions": ad.total_impressions,
            "clicks": ad.total_clicks,
        }

        # Generate optimization
        ad_content = {
            "headline": ad.headline,
            "description": ad.description,
            "images": ad.images or [],
            "cta": ad.call_to_action,
        }

        optimization = await self.orchestrator.optimize_ad(
            vehicle_data=vehicle.__dict__,
            ad_content=ad_content,
            current_metrics=current_metrics,
            goals={}
        )

        self.metrics["optimizations_performed"] += 1
        return optimization

    async def generate_ad_preview(
        self,
        preview_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate ad preview HTML.

        Args:
            preview_data: Preview data dictionary
            db: Database session

        Returns:
            Preview HTML and URL
        """
        # Build preview HTML based on platform
        preview_html = self._build_preview_html(preview_data)
        platform = preview_data.get("platform", AdPlatform.FACEBOOK)
        preview_url = f"/api/v1/ads/preview/{platform.value}"

        return {
            "preview_html": preview_html,
            "preview_url": preview_url,
        }

    def _is_valid_status_transition(
        self,
        current_status: AdStatus,
        new_status: AdStatus
    ) -> bool:
        """
        Validate status transitions.

        Args:
            current_status: Current ad status
            new_status: Desired new status

        Returns:
            True if transition is valid
        """
        valid_transitions = {
            AdStatus.DRAFT: [
                AdStatus.SCHEDULED,
                AdStatus.ACTIVE,
                AdStatus.CANCELLED
            ],
            AdStatus.SCHEDULED: [
                AdStatus.ACTIVE,
                AdStatus.PAUSED,
                AdStatus.CANCELLED
            ],
            AdStatus.ACTIVE: [
                AdStatus.PAUSED,
                AdStatus.COMPLETED,
                AdStatus.CANCELLED
            ],
            AdStatus.PAUSED: [
                AdStatus.ACTIVE,
                AdStatus.CANCELLED
            ],
            AdStatus.COMPLETED: [],  # Terminal state
            AdStatus.CANCELLED: [],  # Terminal state
        }

        return new_status in valid_transitions.get(current_status, [])

    async def _generate_ai_suggestions(
        self,
        vehicle: Vehicle,
        ad: Ad
    ) -> Dict[str, Any]:
        """
        Generate AI suggestions for new ad.

        Args:
            vehicle: Vehicle object
            ad: Ad object

        Returns:
            AI suggestions dictionary
        """
        # Use GeneratorAgent from orchestrator
        ad_content = {
            "headline": ad.headline,
            "description": ad.description,
        }

        try:
            result = await self.orchestrator.generate_ad_content(
                vehicle_data=vehicle.__dict__,
                content_type="full"
            )

            return {
                "headlines": [result.get("headline", ad.headline)],
                "descriptions": [result.get("description", ad.description)],
                "ctas": [result.get("cta", ad.call_to_action)],
                "estimated_ctr": {"min": 0.035, "max": 0.045},
                "estimated_impressions": 1000,
            }
        except Exception as e:
            # Fallback to basic suggestions if AI fails
            return {
                "headlines": [ad.headline or "Great Deal"],
                "descriptions": [ad.description or "Check out this vehicle"],
                "ctas": [ad.call_to_action or "Learn More"],
                "estimated_ctr": {"min": 0.025, "max": 0.035},
                "estimated_impressions": 500,
            }

    def _build_preview_html(self, data: Dict[str, Any]) -> str:
        """
        Build preview HTML based on platform.

        Args:
            data: Preview data

        Returns:
            HTML string
        """
        platform = data.get("platform", AdPlatform.FACEBOOK)

        if platform == AdPlatform.FACEBOOK:
            return self._facebook_preview_html(data)
        elif platform == AdPlatform.INSTAGRAM:
            return self._instagram_preview_html(data)
        elif platform == AdPlatform.GOOGLE:
            return self._google_preview_html(data)

        return "<div>Preview not available</div>"

    def _facebook_preview_html(self, data: Dict[str, Any]) -> str:
        """
        Generate Facebook ad preview HTML.

        Args:
            data: Preview data

        Returns:
            HTML string
        """
        images = data.get('images', [])
        image_url = images[0] if images else ''
        image_html = (
            f'<img src="{image_url}" style="width: 100%; height: 100%; object-fit: cover;" />'
            if image_url
            else '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">No Image</div>'
        )
        headline = data.get('headline', 'Your Headline')
        description = data.get('description', 'Check out this amazing vehicle offer! Don\'t miss out on this incredible deal.')
        cta = data.get('call_to_action', 'Learn More')

        return f'''
        <div class="fb-ad-preview" style="border: 1px solid #ddd; padding: 16px; max-width: 500px; font-family: Helvetica, Arial, sans-serif;">
            <div style="display: flex; gap: 12px;">
                <div style="width: 120px; height: 120px; background: #f0f0f0; border-radius: 8px; overflow: hidden;">
                    {image_html}
                </div>
                <div style="flex: 1;">
                    <div style="font-size: 12px; color: #606770; margin-bottom: 4px;">Sponsored</div>
                    <div style="font-weight: 600; margin: 4px 0; font-size: 16px;">{headline}</div>
                    <div style="font-size: 12px; color: #606770; margin: 4px 0; line-height: 1.4;">
                        {description}
                    </div>
                    <div style="margin-top: 8px;">
                        <button style="background: #E4E6EB; border: none; padding: 8px 12px; border-radius: 6px; font-weight: 600; font-size: 14px; cursor: pointer;">
                            {cta}
                        </button>
                    </div>
                </div>
            </div>
        </div>
        '''

    def _instagram_preview_html(self, data: Dict[str, Any]) -> str:
        """
        Generate Instagram ad preview HTML.

        Args:
            data: Preview data

        Returns:
            HTML string
        """
        images = data.get('images', [])
        image_url = images[0] if images else ''
        image_html = (
            f'<img src="{image_url}" style="width: 100%; height: 100%; object-fit: cover;" />'
            if image_url
            else '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">No Image</div>'
        )
        headline = data.get('headline', 'Your Headline')
        description = data.get('description', '')
        cta = data.get('call_to_action', 'Learn More')

        return f'''
        <div class="ig-ad-preview" style="border: 1px solid #ddd; padding: 16px; max-width: 400px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div style="width: 32px; height: 32px; background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); border-radius: 50%; margin-right: 8px;"></div>
                <div>
                    <div style="font-weight: 600; font-size: 14px;">Sponsored</div>
                    <div style="font-size: 11px; color: #8e8e8e;">Sponsored • See more</div>
                </div>
            </div>
            <div style="width: 100%; height: 300px; background: #fafafa; border-radius: 8px; overflow: hidden; margin-bottom: 12px;">
                {image_html}
            </div>
            <div style="font-size: 14px; margin-bottom: 8px;">
                <span style="font-weight: 600;">{headline}</span>
                <span style="margin-left: 4px;">{description}</span>
            </div>
            <button style="background: #0095f6; border: none; padding: 6px 16px; border-radius: 4px; font-weight: 600; font-size: 14px; color: white; cursor: pointer;">
                {cta}
            </button>
        </div>
        '''

    def _google_preview_html(self, data: Dict[str, Any]) -> str:
        """
        Generate Google ad preview HTML.

        Args:
            data: Preview data

        Returns:
            HTML string
        """
        return f'''
        <div class="google-ad-preview" style="border: 1px solid #ddd; padding: 16px; max-width: 600px; font-family: Arial, sans-serif;">
            <div style="margin-bottom: 12px;">
                <span style="color: #202124; font-size: 20px; font-weight: 400;">{data.get('headline', 'Your Headline')}</span>
                <span style="color: #202124; font-size: 20px; font-weight: 400;"> | {data.get('description', 'Your description here')}</span>
            </div>
            <div style="color: #4d5156; font-size: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <div style="width: 28px; height: 28px; background: #f1f3f4; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px;">A</div>
                    <div>
                        <div style="color: #202124; font-size: 14px;">www.example.com</div>
                        <div style="color: #4d5156;">{data.get('description', 'Your ad description text appears here with more details about your offer.')} · <span style="color: #1a0dab;">{data.get('call_to_action', 'Learn More')}</span></div>
                    </div>
                </div>
            </div>
        </div>
        '''

    async def _get_ad(self, ad_id: UUID, db: AsyncSession) -> Ad:
        """
        Get ad by ID.

        Args:
            ad_id: Ad ID
            db: Database session

        Returns:
            Ad object

        Raises:
            ValueError: If ad not found
        """
        result = await db.execute(
            select(Ad).where(Ad.id == ad_id).where(Ad.deleted_at.is_(None))
        )
        ad = result.scalar_one_or_none()
        if not ad:
            raise ValueError(f"Ad {ad_id} not found")
        return ad

    async def _get_vehicle(self, vehicle_id: UUID, db: AsyncSession) -> Vehicle:
        """
        Get vehicle by ID.

        Args:
            vehicle_id: Vehicle ID
            db: Database session

        Returns:
            Vehicle object

        Raises:
            ValueError: If vehicle not found
        """
        result = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        return vehicle
