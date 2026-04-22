"""
Facebook integration endpoints.
"""
import logging
import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.deps import get_current_user, get_db, get_current_dealership
from app.models.facebook_account import FacebookAccount
from app.models.facebook_token import FacebookToken
from app.models.user import User
from app.models.dealership import Dealership
from app.schemas.facebook import (
    FacebookOAuthURL,
    FacebookAccountResponse,
    FacebookAccountInfo,
    FacebookMetricsSync,
    FacebookMetricsResponse,
)
from app.services.facebook_service import FacebookIntegrationService
from app.services.facebook_metrics_service import FacebookMetricsSync


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/connect", response_model=FacebookOAuthURL)
async def connect_facebook(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Initiate Facebook OAuth flow.

    Returns authorization URL for user to grant permissions.
    """
    try:
        service = FacebookIntegrationService(db)

        oauth_data = await service.generate_oauth_url(
            dealership_id=current_dealership.id
        )

        return oauth_data

    except Exception as e:
        logger.error(f"Error initiating Facebook OAuth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}",
        )


@router.get("/callback")
async def facebook_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="OAuth state parameter"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Handle Facebook OAuth callback.

    Exchange authorization code for access token and retrieve ad accounts.
    """
    try:
        service = FacebookIntegrationService(db)

        # Exchange code for token
        token = await service.exchange_code_for_token(
            code=code,
            dealership_id=current_dealership.id,
            user_id=current_user.id
        )

        # Get user's ad accounts
        accounts = await service.get_user_ad_accounts(
            access_token=token.access_token
        )

        # Return accounts for user to select
        return {
            "message": "Successfully connected to Facebook",
            "token_id": token.id,
            "accounts": accounts,
            "next_step": "Select an account to connect",
        }

    except Exception as e:
        logger.error(f"Error in Facebook callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete OAuth flow: {str(e)}",
        )


@router.get("/accounts", response_model=List[FacebookAccountInfo])
async def list_facebook_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    List all Facebook ad accounts connected to dealership.
    """
    try:
        result = await db.execute(
            select(FacebookAccount).where(
                FacebookAccount.dealership_id == current_dealership.id,
                FacebookAccount.deleted_at.is_(None)
            )
        )
        accounts = result.scalars().all()

        return [
            FacebookAccountInfo(
                account_id=acc.facebook_account_id,
                account_name=acc.facebook_account_name,
                account_status=1 if acc.status.value == "active" else 0,
                currency=acc.account_metadata.get("currency", "BRL")
                if acc.account_metadata else "BRL",
                timezone_name=acc.account_metadata.get("timezone_name", "America/Sao_Paulo")
                if acc.account_metadata else "America/Sao_Paulo",
                timezone_offset_hours_utc=acc.account_metadata.get("timezone_offset_hours_utc", -3)
                if acc.account_metadata else -3,
                business_name=acc.account_metadata.get("business_name")
                if acc.account_metadata else None,
                business_id=acc.facebook_business_id,
            )
            for acc in accounts
        ]

    except Exception as e:
        logger.error(f"Error listing Facebook accounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list accounts: {str(e)}",
        )


@router.post("/accounts/{facebook_account_id}/connect", response_model=FacebookAccountResponse)
async def connect_facebook_account(
    facebook_account_id: str,
    access_token: str = Query(..., description="Facebook access token"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Connect a specific Facebook ad account to dealership.

    This should be called after user selects an account from the list returned by callback.
    """
    try:
        service = FacebookIntegrationService(db)

        # Get account info from Facebook
        accounts = await service.get_user_ad_accounts(access_token=access_token)

        selected_account = None
        for acc in accounts:
            if acc["account_id"] == facebook_account_id:
                selected_account = acc
                break

        if not selected_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {facebook_account_id} not found in user's accounts",
            )

        # Connect account
        facebook_account = await service.connect_account(
            dealership_id=current_dealership.id,
            facebook_account_id=facebook_account_id,
            access_token=access_token,
            account_info=selected_account,
        )

        return facebook_account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting Facebook account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect account: {str(e)}",
        )


@router.delete("/accounts/{account_id}")
async def disconnect_facebook_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Disconnect a Facebook ad account from dealership.
    """
    try:
        service = FacebookIntegrationService(db)

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
async def get_facebook_account_status(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Get status of connected Facebook ad account.
    """
    try:
        result = await db.execute(
            select(FacebookAccount).where(
                FacebookAccount.id == account_id,
                FacebookAccount.dealership_id == current_dealership.id,
                FacebookAccount.deleted_at.is_(None)
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        return {
            "account_id": account.facebook_account_id,
            "account_name": account.facebook_account_name,
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


@router.post("/sync/{facebook_account_id}/metrics", response_model=FacebookMetricsResponse)
async def sync_facebook_metrics(
    facebook_account_id: str,
    sync_data: FacebookMetricsSync,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Sync metrics from Facebook Ads account.

    Trigger manual sync of metrics for all ads or specific ads.
    """
    try:
        from app.services.facebook_metrics_service import FacebookMetricsSync as MetricsSync

        sync_service = MetricsSync(db)

        result = await sync_service.sync_account_metrics(
            facebook_account_id=facebook_account_id,
            start_date=sync_data.start_date,
            end_date=sync_data.end_date,
            ad_ids=sync_data.ad_ids
        )

        return FacebookMetricsResponse(
            success=result["success"],
            account_id=result["account_id"],
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
    facebook_account_id: str = Query(..., description="Facebook Ad Account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_dealership: Dealership = Depends(get_current_dealership),
):
    """
    Get real-time metrics for a specific ad.

    Returns current day metrics from Facebook Ads.
    """
    try:
        from app.services.facebook_metrics_service import FacebookMetricsSync as MetricsSync
        from uuid import UUID

        sync_service = MetricsSync(db)

        metrics = await sync_service.get_realtime_metrics(
            internal_ad_id=UUID(ad_id),
            facebook_account_id=facebook_account_id
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
