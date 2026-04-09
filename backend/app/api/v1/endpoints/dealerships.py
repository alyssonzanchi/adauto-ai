"""
Dealerships CRUD endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.models import Dealership, User
from app.models.enums import UserRole, DealershipStatus
from app.schemas.dealership import (
    DealershipResponse,
    DealershipUpdate,
    DealershipCreate,
)
from app.schemas.user import UserResponse
from app.schemas.filters import DealershipFilter
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DealershipResponse])
async def list_dealerships(
    pagination: PaginationParams = Depends(),
    filters: DealershipFilter = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all dealerships with pagination and filters.

    Args:
        pagination: Pagination parameters
        filters: Filter parameters
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of dealerships
    """
    # Build base query
    query = select(Dealership)

    # Non-admin users can only see their own dealership
    if current_user.role != UserRole.ADMIN:
        query = query.where(Dealership.id == current_user.dealership_id)

    # Apply filters
    if filters.name:
        query = query.where(Dealership.name.ilike(f"%{filters.name}%"))
    if filters.email:
        query = query.where(Dealership.email.ilike(f"%{filters.email}%"))
    if filters.document_id:
        query = query.where(Dealership.document_id.ilike(f"%{filters.document_id}%"))
    if filters.status:
        query = query.where(Dealership.status == filters.status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    query = query.offset(pagination.skip).limit(pagination.limit)

    # Execute query
    result = await db.execute(query)
    dealerships = result.scalars().all()

    # Calculate total pages
    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=dealerships,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/{dealership_id}", response_model=DealershipResponse)
async def get_dealership(
    dealership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dealership by ID.

    Args:
        dealership_id: Dealership ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dealership data

    Raises:
        HTTPException: If dealership not found or no permission
    """
    result = await db.execute(
        select(Dealership).where(Dealership.id == dealership_id)
    )
    dealership = result.scalar_one_or_none()

    if not dealership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealership not found"
        )

    # Check permission - non-admin can only see their own dealership
    if (current_user.role != UserRole.ADMIN and
        dealership.id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return dealership


@router.post("", response_model=DealershipResponse, status_code=status.HTTP_201_CREATED)
async def create_dealership(
    dealership_data: DealershipCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new dealership (admin only).

    Args:
        dealership_data: Dealership data
        current_user: Current authenticated user (admin only)
        db: Database session

    Returns:
        Created dealership

    Raises:
        HTTPException: If email or document_id already exists
    """
    # Check if email already exists
    result = await db.execute(
        select(Dealership).where(Dealership.email == dealership_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if document_id already exists
    result = await db.execute(
        select(Dealership).where(
            Dealership.document_id == dealership_data.document_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document ID already registered"
        )

    # Create dealership
    dealership = Dealership(
        name=dealership_data.name,
        trade_name=dealership_data.trade_name,
        document_id=dealership_data.document_id,
        state_registration=dealership_data.state_registration,
        email=dealership_data.email,
        phone=dealership_data.phone,
        whatsapp=dealership_data.whatsapp,
        website=dealership_data.website,
        address=dealership_data.address,
        settings=dealership_data.settings,
        status=DealershipStatus.ACTIVE,
    )

    db.add(dealership)
    await db.commit()
    await db.refresh(dealership)

    return dealership


@router.put("/{dealership_id}", response_model=DealershipResponse)
async def update_dealership(
    dealership_id: UUID,
    dealership_data: DealershipUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update dealership.

    Args:
        dealership_id: Dealership ID
        dealership_data: Updated dealership data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated dealership

    Raises:
        HTTPException: If dealership not found or no permission
    """
    result = await db.execute(
        select(Dealership).where(Dealership.id == dealership_id)
    )
    dealership = result.scalar_one_or_none()

    if not dealership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealership not found"
        )

    # Check permission - non-admin can only edit their own dealership
    if (current_user.role != UserRole.ADMIN and
        dealership.id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
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

    # Update fields
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


@router.delete("/{dealership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dealership(
    dealership_id: UUID,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete dealership (soft delete, admin only).

    Args:
        dealership_id: Dealership ID
        current_user: Current authenticated user (admin only)
        db: Database session

    Raises:
        HTTPException: If dealership not found or trying to delete own dealership
    """
    result = await db.execute(
        select(Dealership).where(Dealership.id == dealership_id)
    )
    dealership = result.scalar_one_or_none()

    if not dealership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealership not found"
        )

    # Prevent deleting your own dealership
    if dealership.id == current_user.dealership_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own dealership"
        )

    # Soft delete
    from datetime import datetime
    dealership.deleted_at = datetime.utcnow()
    dealership.status = DealershipStatus.SUSPENDED

    await db.commit()


@router.patch("/{dealership_id}/activate", response_model=DealershipResponse)
async def activate_dealership(
    dealership_id: UUID,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate dealership account (admin only).

    Args:
        dealership_id: Dealership ID
        current_user: Current authenticated user (admin only)
        db: Database session

    Returns:
        Updated dealership

    Raises:
        HTTPException: If dealership not found
    """
    result = await db.execute(
        select(Dealership).where(Dealership.id == dealership_id)
    )
    dealership = result.scalar_one_or_none()

    if not dealership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealership not found"
        )

    dealership.status = DealershipStatus.ACTIVE
    await db.commit()
    await db.refresh(dealership)

    return dealership


@router.patch("/{dealership_id}/suspend", response_model=DealershipResponse)
async def suspend_dealership(
    dealership_id: UUID,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Suspend dealership account (admin only).

    Args:
        dealership_id: Dealership ID
        current_user: Current authenticated user (admin only)
        db: Database session

    Returns:
        Updated dealership

    Raises:
        HTTPException: If dealership not found or trying to suspend own dealership
    """
    result = await db.execute(
        select(Dealership).where(Dealership.id == dealership_id)
    )
    dealership = result.scalar_one_or_none()

    if not dealership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealership not found"
        )

    # Prevent suspending your own dealership
    if dealership.id == current_user.dealership_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend your own dealership"
        )

    dealership.status = DealershipStatus.SUSPENDED
    await db.commit()
    await db.refresh(dealership)

    return dealership


@router.get("/{dealership_id}/users", response_model=List[UserResponse])
async def get_dealership_users(
    dealership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all users from a dealership.

    Args:
        dealership_id: Dealership ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of users

    Raises:
        HTTPException: If dealership not found or no permission
    """
    # Check if dealership exists
    result = await db.execute(
        select(Dealership).where(Dealership.id == dealership_id)
    )
    dealership = result.scalar_one_or_none()

    if not dealership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealership not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get users
    result = await db.execute(
        select(User)
        .where(User.dealership_id == dealership_id)
        .where(User.deleted_at.is_(None))
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return users
