"""
Ads endpoints.
"""
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_current_manager_or_admin
from app.core.database import get_db
from app.models import User
from app.models.enums import UserRole, AdStatus
from app.schemas.ad import (
    AdResponse,
    AdCreate,
    AdUpdate,
    AdStatusUpdate,
    AdFilter,
    AdPreviewRequest,
    AdPreviewResponse,
)
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services.ad_service import AdService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AdResponse])
async def list_ads(
    pagination: PaginationParams = Depends(),
    filters: AdFilter = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all ads with pagination and filters.

    Non-admin users see only their dealership's ads.
    """
    query = select(Ad).where(Ad.deleted_at.is_(None))

    # Non-admin users see only their dealership's ads
    if current_user.role != UserRole.ADMIN:
        from app.models.vehicle import Vehicle
        query = query.join(Vehicle).where(
            Vehicle.dealership_id == current_user.dealership_id
        )

    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(
                Ad.title.ilike(search_term),
                Ad.description.ilike(search_term),
                Ad.headline.ilike(search_term),
            )
        )

    if filters.platform:
        query = query.where(Ad.platform == filters.platform.value)

    if filters.status:
        query = query.where(Ad.status == filters.status.value)

    if filters.vehicle_id:
        query = query.where(Ad.vehicle_id == filters.vehicle_id)

    if filters.start_date_min:
        query = query.where(Ad.start_date >= filters.start_date_min)

    if filters.start_date_max:
        query = query.where(Ad.start_date <= filters.start_date_max)

    if filters.ai_generated is not None:
        query = query.where(Ad.ai_generated == filters.ai_generated)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    query = query.order_by(Ad.created_at.desc())
    query = query.offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(query)
    ads = result.scalars().all()

    return PaginatedResponse.create(
        items=ads,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get("/{ad_id}", response_model=AdResponse)
async def get_ad(
    ad_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get ad by ID.

    Non-admin users can only see their dealership's ads.
    """
    from app.models.ad import Ad

    query = select(Ad).where(Ad.id == ad_id).where(Ad.deleted_at.is_(None))

    # Non-admin users can only see their dealership's ads
    if current_user.role != UserRole.ADMIN:
        from app.models.vehicle import Vehicle
        query = query.join(Vehicle).where(
            Vehicle.dealership_id == current_user.dealership_id
        )

    result = await db.execute(query)
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )

    return ad


@router.post("", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
async def create_ad(
    ad_data: AdCreate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new ad.

    Only managers and admins can create ads.
    """
    from app.models.vehicle import Vehicle
    from app.models.ad import Ad

    # Validate vehicle ownership
    vehicle_result = await db.execute(
        select(Vehicle).where(Vehicle.id == ad_data.vehicle_id)
    )
    vehicle = vehicle_result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    if current_user.role != UserRole.ADMIN and vehicle.dealership_id != current_user.dealership_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Create ad
    ad_service = AdService()
    try:
        ad = await ad_service.create_ad(ad_data.dict(), db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return ad


@router.put("/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: UUID,
    ad_data: AdUpdate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update ad.

    Only managers and admins can update ads.
    """
    from app.models.ad import Ad

    result = await db.execute(
        select(Ad).where(Ad.id == ad_id).where(Ad.deleted_at.is_(None))
    )
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )

    # Check permissions
    if current_user.role != UserRole.ADMIN:
        from app.models.vehicle import Vehicle
        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.id == ad.vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()

        if vehicle.dealership_id != current_user.dealership_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    # Update fields
    update_data = ad_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ad, field, value)

    await db.commit()
    await db.refresh(ad)

    return ad


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(
    ad_id: UUID,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete ad (soft delete).

    Only managers and admins can delete ads.
    """
    from app.models.ad import Ad

    result = await db.execute(
        select(Ad).where(Ad.id == ad_id).where(Ad.deleted_at.is_(None))
    )
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )

    # Check permissions
    if current_user.role != UserRole.ADMIN:
        from app.models.vehicle import Vehicle
        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.id == ad.vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()

        if vehicle.dealership_id != current_user.dealership_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    # Soft delete
    ad.deleted_at = datetime.utcnow()
    await db.commit()


@router.patch("/{ad_id}/status", response_model=AdResponse)
async def update_ad_status(
    ad_id: UUID,
    status_data: AdStatusUpdate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update ad status.

    Only managers and admins can update ad status.
    """
    from app.models.ad import Ad

    # Get ad with permission check
    query = select(Ad).where(Ad.id == ad_id).where(Ad.deleted_at.is_(None))

    if current_user.role != UserRole.ADMIN:
        from app.models.vehicle import Vehicle
        query = query.join(Vehicle).where(
            Vehicle.dealership_id == current_user.dealership_id
        )

    result = await db.execute(query)
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )

    # Update status via service
    ad_service = AdService()
    try:
        ad = await ad_service.update_ad_status(
            ad_id,
            status_data.status,
            status_data.reason,
            db
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return ad


@router.post("/{ad_id}/optimize")
async def optimize_ad(
    ad_id: UUID,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate optimization suggestions for ad.

    Only managers and admins can optimize ads.
    """
    from app.models.ad import Ad

    # Get ad with permission check
    query = select(Ad).where(Ad.id == ad_id).where(Ad.deleted_at.is_(None))

    if current_user.role != UserRole.ADMIN:
        from app.models.vehicle import Vehicle
        query = query.join(Vehicle).where(
            Vehicle.dealership_id == current_user.dealership_id
        )

    result = await db.execute(query)
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )

    # Generate optimization
    ad_service = AdService()
    try:
        optimization = await ad_service.optimize_ad(ad_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return optimization


@router.post("/preview", response_model=AdPreviewResponse)
async def generate_ad_preview(
    preview_data: AdPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate ad preview.

    All authenticated users can generate previews.
    """
    ad_service = AdService()
    preview = await ad_service.generate_ad_preview(preview_data.dict(), db)

    return preview
