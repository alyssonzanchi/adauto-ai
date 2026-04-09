"""
Users CRUD endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import (
    get_current_admin,
    get_current_manager_or_admin,
    get_current_user,
)
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models import User, Dealership
from app.models.enums import UserRole, UserStatus
from app.schemas.filters import UserFilter
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.user import UserResponse, UserUpdate, UserChangePassword

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    filters: UserFilter = Depends(),
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users with pagination and filters.

    Args:
        pagination: Pagination parameters
        filters: Filter parameters
        current_user: Current authenticated user (manager or admin)
        db: Database session

    Returns:
        Paginated list of users

    Raises:
        HTTPException: If user doesn't have permission
    """
    # Build base query - managers can only see users from their dealership
    query = select(User)

    # If not admin, filter by dealership_id
    if current_user.role != UserRole.ADMIN:
        query = query.where(User.dealership_id == current_user.dealership_id)

    # Apply filters
    if filters.email:
        query = query.where(User.email.ilike(f"%{filters.email}%"))
    if filters.name:
        query = query.where(User.name.ilike(f"%{filters.name}%"))
    if filters.role:
        query = query.where(User.role == filters.role)
    if filters.status:
        query = query.where(User.status == filters.status)
    if filters.dealership_id and current_user.role == UserRole.ADMIN:
        query = query.where(User.dealership_id == UUID(filters.dealership_id))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    query = query.offset(pagination.skip).limit(pagination.limit)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Calculate total pages
    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=users,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID.

    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: If user not found or no permission
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permission - users can only see users from their dealership
    if (current_user.role != UserRole.ADMIN and
        user.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user.

    Args:
        user_id: User ID
        user_data: Updated user data
        current_user: Current authenticated user (manager or admin)
        db: Database session

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found or no permission
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        user.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Check if email is being changed and if it's already in use
    if user_data.email and user_data.email != user.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = user_data.email

    # Update fields
    if user_data.name:
        user.name = user_data.name
    if user_data.phone:
        user.phone = user_data.phone

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user (soft delete).

    Args:
        user_id: User ID
        current_user: Current authenticated user (admin only)
        db: Database session

    Raises:
        HTTPException: If user not found or trying to delete yourself
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    # Soft delete
    from datetime import datetime
    user.deleted_at = datetime.utcnow()
    user.status = UserStatus.INACTIVE

    await db.commit()


@router.post("/{user_id}/change-password")
async def change_user_password(
    user_id: UUID,
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password.

    Args:
        user_id: User ID
        password_data: Old and new passwords
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found, wrong password, or no permission
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Users can only change their own password unless they're admin/manager
    if (current_user.role not in [UserRole.ADMIN, UserRole.MANAGER] and
        user.id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Verify old password
    if not verify_password(password_data.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate user account.

    Args:
        user_id: User ID
        current_user: Current authenticated user (manager or admin)
        db: Database session

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found or no permission
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        user.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    user.status = UserStatus.ACTIVE
    await db.commit()
    await db.refresh(user)

    return user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate user account.

    Args:
        user_id: User ID
        current_user: Current authenticated user (manager or admin)
        db: Database session

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found or no permission
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deactivating yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        user.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    user.status = UserStatus.INACTIVE
    await db.commit()
    await db.refresh(user)

    return user
