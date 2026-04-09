"""
Profile management endpoints.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserResponse, UserUpdate, UserChangePassword
from app.schemas.dealership import DealershipResponse, DealershipUpdate

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_my_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user profile.

    Args:
        profile_data: Updated profile data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user data

    Raises:
        HTTPException: If email already in use
    """
    # Check if email is being changed and if it's already in use
    if profile_data.email and profile_data.email != current_user.email:
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.email == profile_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = profile_data.email

    # Update fields
    if profile_data.name:
        current_user.name = profile_data.name
    if profile_data.phone:
        current_user.phone = profile_data.phone

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/profile/change-password")
async def change_my_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change current user password.

    Args:
        password_data: Old and new passwords
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If old password is incorrect
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.get("/profile/dealership", response_model=DealershipResponse)
async def get_my_dealership(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's dealership.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dealership data

    Raises:
        HTTPException: If dealership not found
    """
    from sqlalchemy import select
    from app.models import Dealership

    result = await db.execute(
        select(Dealership).where(Dealership.id == current_user.dealership_id)
    )
    dealership = result.scalar_one_or_none()

    if not dealership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealership not found"
        )

    return dealership


@router.put("/profile/dealership", response_model=DealershipResponse)
async def update_my_dealership(
    dealership_data: DealershipUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's dealership.

    Args:
        dealership_data: Updated dealership data
        current_user: Current authenticated user (manager or admin only)
        db: Database session

    Returns:
        Updated dealership data

    Raises:
        HTTPException: If no permission, dealership not found, or email in use
    """
    from sqlalchemy import select
    from app.models import Dealership, UserRole

    # Only managers and admins can update dealership
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get dealership
    result = await db.execute(
        select(Dealership).where(Dealership.id == current_user.dealership_id)
    )
    dealership = result.scalar_one_or_none()

    if not dealership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealership not found"
        )

    # Check if email is being changed and if it's already in use
    if dealership_data.email is not None and dealership_data.email != dealership.email:
        result = await db.execute(
            select(Dealership).where(Dealership.email == dealership_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        dealership.email = dealership_data.email

    # Update fields (non-admin cannot change status)
    if dealership_data.name is not None:
        dealership.name = dealership_data.name
    if dealership_data.trade_name is not None:
        dealership.trade_name = dealership_data.trade_name
    if dealership_data.phone is not None:
        dealership.phone = dealership_data.phone
    if dealership_data.whatsapp is not None:
        dealership.whatsapp = dealership_data.whatsapp
    if dealership_data.website is not None:
        dealership.website = dealership_data.website
    if dealership_data.address is not None:
        dealership.address = dealership_data.address
    if dealership_data.settings is not None:
        dealership.settings = dealership_data.settings
    if dealership_data.status is not None and current_user.role == UserRole.ADMIN:
        dealership.status = dealership_data.status

    await db.commit()
    await db.refresh(dealership)

    return dealership
