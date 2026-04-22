"""
Google Ads integration endpoints.
"""
import logging
import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.deps import get_current_user, get_db, get_current_dealership
from app.models.google_account import GoogleAccount
from app.models.google_token import GoogleToken
from app.models.user import User
from app.models.dealership import Dealership
from app.schemas.google import (
    GoogleOAuthURL,
    GoogleAccountResponse,
    GoogleAdAccountInfo,
    GoogleMetricsSync,
    GoogleMetricsResponse,
)


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/connect", response_model=GoogleOAuthURL)
async def connect_google_ads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Initiate Google Ads OAuth flow.

    Returns authorization URL for user to grant permissions.
    """
    try:
        from app.services.google_service import GoogleIntegrationService

        service = GoogleIntegrationService(db)

        oauth_data = await service.generate_oauth_url(
            dealership_id=current_dealership.id
        )

        return oauth_data

    except Exception as e:
        logger.error(f"Error initiating Google Ads OAuth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}",
        )


@router.get("/callback")
async def google_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="OAuth state parameter"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Handle Google Ads OAuth callback.

    Exchange authorization code for access token and retrieve ad accounts.
    """
    try:
        from app.services.google_service import GoogleIntegrationService

        service = GoogleIntegrationService(db)

        # Exchange code for token
        token = await service.exchange_code_for_token(
            code=code,
            dealership_id=current_dealership.id,
            user_id=current_user.id
        )

        # Get accessible accounts
        accounts = await service.get_accessible_accounts(
            access_token=token.access_token,
            refresh_token=token.refresh_token
        )

        # Return accounts for user to select
        return {
            "message": "Successfully connected to Google Ads",
            "token_id": token.id,
            "accounts": accounts,
            "next_step": "Select an account to connect",
        }

    except Exception as e:
        logger.error(f"Error in Google Ads callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete OAuth flow: {str(e)}",
        )


@router.get("/accounts", response_model=List[GoogleAdAccountInfo])
async def list_google_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    List all Google Ads accounts connected to dealership.
    """
    try:
        result = await db.execute(
            select(GoogleAccount).where(
                GoogleAccount.dealership_id == current_dealership.id,
                GoogleAccount.deleted_at.is_(None)
            )
        )
        accounts = result.scalars().all()

        return [
            GoogleAdAccountInfo(
                customer_id=acc.google_account_id,
                account_name=acc.google_account_name,
                currency_code=acc.account_metadata.get("currency_code", "USD")
                if acc.account_metadata else "USD",
                time_zone=acc.account_metadata.get("time_zone", "UTC")
                if acc.account_metadata else "UTC",
                tracking_url_template=acc.account_metadata.get("tracking_url_template")
                if acc.account_metadata else None,
                final_url_suffix=acc.account_metadata.get("final_url_suffix")
                if acc.account_metadata else None,
                manager_id=acc.google_manager_id,
            )
            for acc in accounts
        ]

    except Exception as e:
        logger.error(f"Error listing Google Ads accounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list accounts: {str(e)}",
        )


@router.post("/accounts/{google_customer_id}/connect", response_model=GoogleAccountResponse)
async def connect_google_account(
    google_customer_id: str,
    access_token: str = Query(..., description="Google access token"),
    refresh_token: str = Query(..., description="Google refresh token"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Connect a specific Google Ads account to dealership.

    This should be called after user selects an account from the list returned by callback.
    """
    try:
        from app.services.google_service import GoogleIntegrationService

        service = GoogleIntegrationService(db)

        # Get account info from Google
        accounts = await service.get_accessible_accounts(
            access_token=access_token,
            refresh_token=refresh_token
        )

        selected_account = None
        for acc in accounts:
            if acc["customer_id"] == google_customer_id:
                selected_account = acc
                break

        if not selected_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {google_customer_id} not found in user's accounts",
            )

        # Connect account
        google_account = await service.connect_account(
            dealership_id=current_dealership.id,
            google_customer_id=google_customer_id,
            access_token=access_token,
            refresh_token=refresh_token,
            account_info=selected_account,
        )

        return google_account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting Google Ads account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect account: {str(e)}",
        )


@router.delete("/accounts/{account_id}")
async def disconnect_google_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Disconnect a Google Ads account from dealership.
    """
    try:
        from app.services.google_service import GoogleIntegrationService

        service = GoogleIntegrationService(db)

        await service.disconnect_account(account_id=account_id)

        return {"message": "Account disconnected successfully"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error disconnecting account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect account: {str(e)}",
        )


@router.get("/accounts/{account_id}/status")
async def get_google_account_status(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Get status of connected Google Ads account.
    """
    try:
        result = await db.execute(
            select(GoogleAccount).where(
                GoogleAccount.id == account_id,
                GoogleAccount.dealership_id == current_dealership.id,
                GoogleAccount.deleted_at.is_(None)
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        return {
            "customer_id": account.google_account_id,
            "account_name": account.google_account_name,
            "status": account.status.value,
            "last_synced_at": account.last_synced_at,
            "auto_sync_enabled": account.auto_sync_enabled,
            "sync_frequency_minutes": account.sync_frequency_minutes,
            "connected_at": account.created_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting account status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account status: {str(e)}",
        )


@router.post("/sync/{google_customer_id}/metrics", response_model=GoogleMetricsResponse)
async def sync_google_metrics(
    google_customer_id: str,
    sync_data: GoogleMetricsSync,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Sync metrics from Google Ads account.

    Trigger manual sync of metrics for all ads or specific ads.
    """
    try:
        from app.services.google_metrics_service import GoogleMetricsSync as MetricsSync

        sync_service = MetricsSync(db)

        result = await sync_service.sync_account_metrics(
            google_customer_id=google_customer_id,
            start_date=sync_data.start_date,
            end_date=sync_data.end_date,
            ad_ids=sync_data.ad_ids
        )

        return GoogleMetricsResponse(
            success=result["success"],
            customer_id=result["customer_id"],
            ads_updated=result["ads_updated"],
            period_start=result.get("period_start") or sync_data.start_date or datetime.datetime.utcnow(),
            period_end=result.get("period_end") or sync_data.end_date or datetime.datetime.utcnow(),
            message=result["message"]
        )

    except Exception as e:
        logger.error(f"Error syncing metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync metrics: {str(e)}",
        )


@router.get("/ads/{ad_id}/metrics")
async def get_ad_realtime_metrics(
    ad_id: str,
    google_customer_id: str = Query(..., description="Google Ads Customer ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Get real-time metrics for a specific ad.

    Returns current day metrics from Google Ads.
    """
    try:
        from app.services.google_metrics_service import GoogleMetricsSync as MetricsSync
        from uuid import UUID

        sync_service = MetricsSync(db)

        metrics = await sync_service.get_realtime_metrics(
            internal_ad_id=UUID(ad_id),
            google_customer_id=google_customer_id
        )

        return metrics

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}",
        )
