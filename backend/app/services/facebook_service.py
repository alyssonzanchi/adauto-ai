"""
Facebook Ads integration service.
"""
import datetime
import logging
import secrets
from typing import Optional, Dict, Any, List
from uuid import UUID

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.exceptions import FacebookRequestError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.facebook_account import FacebookAccount
from app.models.facebook_token import FacebookToken
from app.models.enums import ConnectionStatus


logger = logging.getLogger(__name__)


class FacebookIntegrationService:
    """Service for managing Facebook Ads integration."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_oauth_url(
        self,
        dealership_id: UUID,
        redirect_uri: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate Facebook OAuth authorization URL.

        Args:
            dealership_id: Dealership ID
            redirect_uri: Optional custom redirect URI

        Returns:
            Dictionary with authorization_url and state
        """
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state temporarily in Redis (implement this)
        # await redis.setex(f"oauth_state:{state}", 600, str(dealership_id))

        # OAuth scopes required
        scopes = [
            "ads_management",
            "ads_read",
            "pages_manage_ads",
            "pages_read_engagement",
            "read_insights",
        ]

        # Build authorization URL
        base_url = "https://www.facebook.com/v18.0/dialog/oauth"
        redirect_uri = redirect_uri or settings.FACEBOOK_REDIRECT_URI

        params = {
            "client_id": settings.FACEBOOK_APP_ID,
            "redirect_uri": redirect_uri,
            "scope": ",".join(scopes),
            "response_type": "code",
            "state": state,
        }

        auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

        logger.info(f"Generated OAuth URL for dealership {dealership_id}")

        return {
            "authorization_url": auth_url,
            "state": state,
        }

    async def exchange_code_for_token(
        self,
        code: str,
        dealership_id: UUID,
        user_id: UUID
    ) -> FacebookToken:
        """
        Exchange OAuth code for access token.

        Args:
            code: OAuth authorization code
            dealership_id: Dealership ID
            user_id: User ID who authorized

        Returns:
            FacebookToken object
        """
        try:
            # Initialize Facebook API
            FacebookAdsApi.init(
                app_id=settings.FACEBOOK_APP_ID,
                app_secret=settings.FACEBOOK_APP_SECRET,
                redirect_uri=settings.FACEBOOK_REDIRECT_URI,
            )

            # Exchange code for token
            from facebook_business.adobjects.user import User
            user = User(fbid="me")

            token_response = user.get_access_token(
                code=code,
                redirect_uri=settings.FACEBOOK_REDIRECT_URI,
            )

            # Create token record
            access_token = token_response.get("access_token")
            token_type = token_response.get("token_type", "Bearer")
            expires_in = token_response.get("expires_in")

            # Calculate expiration
            expires_at = None
            if expires_in:
                expires_at = datetime.datetime.utcnow() + datetime.timedelta(
                    seconds=int(expires_in)
                )

            facebook_token = FacebookToken(
                user_id=user_id,
                dealership_id=dealership_id,
                access_token=access_token,
                token_type=token_type,
                expires_in=str(expires_in) if expires_in else None,
                expires_at=expires_at,
                granted_scopes=",".join(self._get_required_scopes()),
            )

            self.db.add(facebook_token)
            await self.db.commit()
            await self.db.refresh(facebook_token)

            logger.info(f"Created Facebook token for dealership {dealership_id}")

            return facebook_token

        except Exception as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            raise

    async def get_user_ad_accounts(
        self,
        access_token: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of user's Facebook ad accounts.

        Args:
            access_token: Facebook access token

        Returns:
            List of ad account information
        """
        try:
            # Initialize API with access token
            FacebookAdsApi.init(access_token=access_token)

            # Get user's ad accounts
            from facebook_business.adobjects.user import User
            user = User(fbid="me")

            accounts = user.get_ad_accounts(
                fields=[
                    AdAccount.Field.account_id,
                    AdAccount.Field.name,
                    AdAccount.Field.account_status,
                    AdAccount.Field.currency,
                    AdAccount.Field.timezone_name,
                    AdAccount.Field.timezone_offset_hours_utc,
                    AdAccount.Field.business_name,
                    AdAccount.Field.business,
                ]
            )

            account_list = []
            for account in accounts:
                account_list.append({
                    "account_id": account[AdAccount.Field.account_id],
                    "account_name": account[AdAccount.Field.name],
                    "account_status": account[AdAccount.Field.account_status],
                    "currency": account[AdAccount.Field.currency],
                    "timezone_name": account[AdAccount.Field.timezone_name],
                    "timezone_offset_hours_utc": account[AdAccount.Field.timezone_offset_hours_utc],
                    "business_name": account.get(AdAccount.Field.business_name),
                    "business_id": account.get(AdAccount.Field.business),
                })

            logger.info(f"Retrieved {len(account_list)} ad accounts")

            return account_list

        except FacebookRequestError as e:
            logger.error(f"Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"Error getting ad accounts: {str(e)}")
            raise

    async def connect_account(
        self,
        dealership_id: UUID,
        facebook_account_id: str,
        access_token: str,
        account_info: Dict[str, Any]
    ) -> FacebookAccount:
        """
        Connect Facebook ad account to dealership.

        Args:
            dealership_id: Dealership ID
            facebook_account_id: Facebook Ad Account ID
            access_token: Facebook access token
            account_info: Account metadata from Facebook

        Returns:
            FacebookAccount object
        """
        try:
            # Check if account already exists
            result = await self.db.execute(
                select(FacebookAccount).where(
                    FacebookAccount.facebook_account_id == facebook_account_id
                )
            )
            existing_account = result.scalar_one_or_none()

            if existing_account:
                # Update existing account
                existing_account.access_token = access_token
                existing_account.status = ConnectionStatus.ACTIVE
                existing_account.account_metadata = account_info

                await self.db.commit()
                await self.db.refresh(existing_account)

                logger.info(f"Updated existing Facebook account {facebook_account_id}")

                return existing_account

            # Create new account connection
            facebook_account = FacebookAccount(
                dealership_id=dealership_id,
                facebook_account_id=facebook_account_id,
                facebook_account_name=account_info.get("account_name"),
                facebook_business_id=account_info.get("business_id"),
                access_token=access_token,
                status=ConnectionStatus.ACTIVE,
                account_metadata=account_info,
            )

            self.db.add(facebook_account)
            await self.db.commit()
            await self.db.refresh(facebook_account)

            logger.info(f"Connected Facebook account {facebook_account_id}")

            return facebook_account

        except Exception as e:
            logger.error(f"Error connecting account: {str(e)}")
            await self.db.rollback()
            raise

    async def disconnect_account(
        self,
        account_id: UUID
    ) -> bool:
        """
        Disconnect Facebook ad account.

        Args:
            account_id: Internal Facebook account ID

        Returns:
            True if successful
        """
        try:
            result = await self.db.execute(
                select(FacebookAccount).where(FacebookAccount.id == account_id)
            )
            account = result.scalar_one_or_none()

            if not account:
                raise ValueError("Account not found")

            # Soft delete
            account.deleted_at = datetime.datetime.utcnow()
            account.status = ConnectionStatus.EXPIRED

            await self.db.commit()

            logger.info(f"Disconnected Facebook account {account_id}")

            return True

        except Exception as e:
            logger.error(f"Error disconnecting account: {str(e)}")
            await self.db.rollback()
            raise

    async def refresh_token(self, account_id: UUID) -> FacebookToken:
        """
        Refresh expired Facebook access token.

        Args:
            account_id: Facebook account ID

        Returns:
            Updated FacebookToken
        """
        # TODO: Implement token refresh logic
        # Facebook tokens typically have long expiration (60 days)
        # but can be refreshed with proper setup
        raise NotImplementedError("Token refresh not implemented")

    def _get_required_scopes(self) -> List[str]:
        """Get required OAuth scopes."""
        return [
            "ads_management",
            "ads_read",
            "pages_manage_ads",
            "pages_read_engagement",
            "read_insights",
        ]
