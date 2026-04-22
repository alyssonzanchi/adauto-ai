"""
Google Ads integration service.
"""
import datetime
import logging
import secrets
from typing import Optional, Dict, Any, List
from uuid import UUID

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.google_account import GoogleAccount
from app.models.google_token import GoogleToken
from app.models.enums import ConnectionStatus


logger = logging.getLogger(__name__)


class GoogleIntegrationService:
    """Service for managing Google Ads integration."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_oauth_flow(self) -> Flow:
        """Create OAuth flow for Google Ads."""
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GOOGLE_ADS_CLIENT_ID,
                    "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_ADS_REDIRECT_URI]
                }
            },
            scopes=[
                "https://www.googleapis.com/auth/adwords"
            ]
        )
        flow.redirect_uri = settings.GOOGLE_ADS_REDIRECT_URI
        return flow

    async def generate_oauth_url(
        self,
        dealership_id: UUID
    ) -> Dict[str, str]:
        """
        Generate Google Ads OAuth authorization URL.

        Args:
            dealership_id: Dealership ID

        Returns:
            Dictionary with authorization_url and state
        """
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state temporarily in Redis (implement this)
        # await redis.setex(f"oauth_state:{state}", 600, str(dealership_id))

        # Create OAuth flow
        flow = self._get_oauth_flow()

        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            state=state,
            prompt="consent"
        )

        logger.info(f"Generated OAuth URL for dealership {dealership_id}")

        return {
            "authorization_url": authorization_url,
            "state": state,
        }

    async def exchange_code_for_token(
        self,
        code: str,
        dealership_id: UUID,
        user_id: UUID
    ) -> GoogleToken:
        """
        Exchange OAuth code for access token.

        Args:
            code: OAuth authorization code
            dealership_id: Dealership ID
            user_id: User ID who authorized

        Returns:
            GoogleToken object
        """
        try:
            # Create OAuth flow
            flow = self._get_oauth_flow()

            # Exchange code for token
            flow.fetch_token(code=code)

            # Get credentials
            credentials = flow.credentials

            # Calculate expiration
            expires_at = None
            if credentials.expiry:
                expires_at = credentials.expiry

            # Create token record
            google_token = GoogleToken(
                user_id=user_id,
                dealership_id=dealership_id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_type="Bearer",
                expires_in=str(credentials.expires_in) if credentials.expires_in else None,
                expires_at=expires_at,
                issued_at=datetime.datetime.utcnow(),
                granted_scopes="https://www.googleapis.com/auth/adwords",
            )

            self.db.add(google_token)
            await self.db.commit()
            await self.db.refresh(google_token)

            logger.info(f"Created Google token for dealership {dealership_id}")

            return google_token

        except Exception as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            raise

    async def get_accessible_accounts(
        self,
        access_token: str,
        refresh_token: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of accessible Google Ads accounts.

        Args:
            access_token: Google access token
            refresh_token: Google refresh token

        Returns:
            List of account information
        """
        try:
            # Create Google Ads client
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_ADS_CLIENT_ID,
                client_secret=settings.GOOGLE_ADS_CLIENT_SECRET
            )

            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=settings.GOOGLE_ADS_DEVELOPER_TOKEN
            )

            # Get Google Ads service
            google_ads_service = client.get_service("GoogleAdsService")

            # Create request to get accessible customers
            request = client.get_type("AccessibleCustomersRequest")
            request.metadata = {}  # Empty metadata

            # Get accessible customers
            response = google_ads_service.get_accessible_customer_ids(request=request)

            account_list = []

            # Get details for each account
            for customer_id in response.resource_names:
                # Extract numeric ID from resource name
                account_id = customer_id.split("/")[-1]

                # Get account details
                account_details = await self._get_account_details(
                    client,
                    account_id
                )

                account_list.append({
                    "customer_id": account_id,
                    "account_name": account_details.get("account_name", ""),
                    "currency_code": account_details.get("currency_code", "USD"),
                    "time_zone": account_details.get("time_zone", "UTC"),
                    "tracking_url_template": account_details.get("tracking_url_template"),
                    "final_url_suffix": account_details.get("final_url_suffix"),
                })

            logger.info(f"Retrieved {len(account_list)} Google Ads accounts")

            return account_list

        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex.error.message()}")
            raise
        except Exception as e:
            logger.error(f"Error getting accounts: {str(e)}")
            raise

    async def _get_account_details(
        self,
        client: GoogleAdsClient,
        customer_id: str
    ) -> Dict[str, Any]:
        """Get details for a specific Google Ads account."""
        try:
            google_ads_service = client.get_service("GoogleAdsService")

            # Create query
            query = f"""
                SELECT
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.tracking_url_template,
                    customer.final_url_suffix
                FROM customer
            """

            # Create request
            request = client.get_type("SearchGoogleAdsRequest")
            request.customer_id = customer_id
            request.query = query

            # Execute query
            response = google_ads_service.search(request=request)

            # Extract details
            for row in response:
                return {
                    "account_name": row.customer.descriptive_name,
                    "currency_code": row.customer.currency_code,
                    "time_zone": row.customer.time_zone,
                    "tracking_url_template": row.customer.tracking_url_template,
                    "final_url_suffix": row.customer.final_url_suffix,
                }

            return {}

        except Exception as e:
            logger.error(f"Error getting account details: {str(e)}")
            return {}

    async def connect_account(
        self,
        dealership_id: UUID,
        google_customer_id: str,
        access_token: str,
        refresh_token: str,
        account_info: Dict[str, Any]
    ) -> GoogleAccount:
        """
        Connect Google Ads account to dealership.

        Args:
            dealership_id: Dealership ID
            google_customer_id: Google Ads Customer ID
            access_token: Google access token
            refresh_token: Google refresh token
            account_info: Account metadata from Google

        Returns:
            GoogleAccount object
        """
        try:
            # Check if account already exists
            result = await self.db.execute(
                select(GoogleAccount).where(
                    GoogleAccount.google_account_id == google_customer_id
                )
            )
            existing_account = result.scalar_one_or_none()

            if existing_account:
                # Update existing account
                existing_account.access_token = access_token
                existing_account.refresh_token = refresh_token
                existing_account.status = ConnectionStatus.ACTIVE
                existing_account.account_metadata = account_info

                await self.db.commit()
                await self.db.refresh(existing_account)

                logger.info(f"Updated existing Google account {google_customer_id}")

                return existing_account

            # Create new account connection
            google_account = GoogleAccount(
                dealership_id=dealership_id,
                google_account_id=google_customer_id,
                google_account_name=account_info.get("account_name"),
                access_token=access_token,
                refresh_token=refresh_token,
                status=ConnectionStatus.ACTIVE,
                account_metadata=account_info,
            )

            self.db.add(google_account)
            await self.db.commit()
            await self.db.refresh(google_account)

            logger.info(f"Connected Google account {google_customer_id}")

            return google_account

        except Exception as e:
            logger.error(f"Error connecting account: {str(e)}")
            await self.db.rollback()
            raise

    async def disconnect_account(
        self,
        account_id: UUID
    ) -> bool:
        """
        Disconnect Google Ads account.

        Args:
            account_id: Internal Google account ID

        Returns:
            True if successful
        """
        try:
            result = await self.db.execute(
                select(GoogleAccount).where(GoogleAccount.id == account_id)
            )
            account = result.scalar_one_or_none()

            if not account:
                raise ValueError("Account not found")

            # Soft delete
            account.deleted_at = datetime.datetime.utcnow()
            account.status = ConnectionStatus.EXPIRED

            await self.db.commit()

            logger.info(f"Disconnected Google account {account_id}")

            return True

        except Exception as e:
            logger.error(f"Error disconnecting account: {str(e)}")
            await self.db.rollback()
            raise

    async def refresh_access_token(self, account_id: UUID) -> GoogleToken:
        """
        Refresh expired Google access token.

        Args:
            account_id: Google account ID

        Returns:
            Updated GoogleToken
        """
        try:
            # Get account
            result = await self.db.execute(
                select(GoogleAccount).where(GoogleAccount.id == account_id)
            )
            account = result.scalar_one_or_none()

            if not account:
                raise ValueError("Account not found")

            # Create credentials with refresh token
            credentials = Credentials(
                token=None,
                refresh_token=account.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_ADS_CLIENT_ID,
                client_secret=settings.GOOGLE_ADS_CLIENT_SECRET
            )

            # Refresh token
            credentials.refresh(None)

            # Update account with new access token
            account.access_token = credentials.token
            account.token_expires_at = credentials.expiry

            await self.db.commit()
            await self.db.refresh(account)

            logger.info(f"Refreshed access token for account {account_id}")

            # Get token from dealership
            result = await self.db.execute(
                select(GoogleToken).where(
                    GoogleToken.dealership_id == account.dealership_id,
                    GoogleToken.is_active == True
                )
            )
            token = result.scalar_one_or_none()

            if token:
                token.access_token = credentials.token
                token.expires_at = credentials.expiry
                await self.db.commit()
                await self.db.refresh(token)

            return token

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise
