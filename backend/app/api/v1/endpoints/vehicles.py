"""
Vehicles CRUD endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_current_manager_or_admin
from app.core.database import get_db
from app.models import Vehicle, User
from app.models.enums import UserRole, VehicleStatus
from app.schemas.vehicle import (
    VehicleResponse,
    VehicleCreate,
    VehicleUpdate,
    VehicleAnalyzeResponse,
    ImageUploadResponse,
    SimilarVehicleResponse,
    SemanticSearchResponse,
)
from app.schemas.filters import VehicleFilter
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services.image_service import image_service
from app.services.ai_service import ai_service  # Keep for backward compatibility
from app.services.ai.orchestrator import get_orchestrator

router = APIRouter()


@router.get("", response_model=PaginatedResponse[VehicleResponse])
async def list_vehicles(
    pagination: PaginationParams = Depends(),
    filters: VehicleFilter = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all vehicles with pagination and filters.

    Non-admin users can only see vehicles from their own dealership.

    Args:
        pagination: Pagination parameters
        filters: Filter parameters
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of vehicles
    """
    # Build base query
    query = select(Vehicle).where(Vehicle.deleted_at.is_(None))

    # Non-admin users can only see vehicles from their dealership
    if current_user.role != UserRole.ADMIN:
        query = query.where(Vehicle.dealership_id == current_user.dealership_id)

    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(
                Vehicle.title.ilike(search_term),
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term),
                Vehicle.description.ilike(search_term),
                Vehicle.plate.ilike(search_term),
            )
        )

    if filters.brand:
        query = query.where(Vehicle.brand.ilike(f"%{filters.brand}%"))

    if filters.model:
        query = query.where(Vehicle.model.ilike(f"%{filters.model}%"))

    if filters.year_min:
        query = query.where(Vehicle.year >= filters.year_min)

    if filters.year_max:
        query = query.where(Vehicle.year <= filters.year_max)

    if filters.price_min:
        query = query.where(Vehicle.price >= filters.price_min)

    if filters.price_max:
        query = query.where(Vehicle.price <= filters.price_max)

    if filters.status:
        query = query.where(Vehicle.status == filters.status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination and ordering
    query = query.order_by(Vehicle.created_at.desc())
    query = query.offset(pagination.skip).limit(pagination.limit)

    # Execute query
    result = await db.execute(query)
    vehicles = result.scalars().all()

    # Calculate total pages
    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=vehicles,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get vehicle by ID.

    Non-admin users can only view vehicles from their own dealership.

    Args:
        vehicle_id: Vehicle ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Vehicle data

    Raises:
        HTTPException: If vehicle not found or no permission
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission - non-admin can only see vehicles from their dealership
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return vehicle


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new vehicle (manager and admin only).

    Args:
        vehicle_data: Vehicle data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created vehicle

    Raises:
        HTTPException: If chassis already exists
    """
    # Check if chassis already exists
    if vehicle_data.chassis:
        result = await db.execute(
            select(Vehicle).where(
                and_(
                    Vehicle.chassis == vehicle_data.chassis,
                    Vehicle.deleted_at.is_(None)
                )
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chassis already registered"
            )

    # Create vehicle
    vehicle = Vehicle(
        dealership_id=current_user.dealership_id,
        title=vehicle_data.title,
        description=vehicle_data.description,
        brand=vehicle_data.brand,
        model=vehicle_data.model,
        year=vehicle_data.year,
        model_year=vehicle_data.model_year,
        version=vehicle_data.version,
        color=vehicle_data.color,
        mileage=vehicle_data.mileage,
        plate=vehicle_data.plate,
        chassis=vehicle_data.chassis,
        doors=vehicle_data.doors,
        seats=vehicle_data.seats,
        fuel_type=vehicle_data.fuel_type.value if vehicle_data.fuel_type else None,
        transmission=vehicle_data.transmission.value if vehicle_data.transmission else None,
        body_type=vehicle_data.body_type.value if vehicle_data.body_type else None,
        price=vehicle_data.price,
        video_url=str(vehicle_data.video_url) if vehicle_data.video_url else None,
        features=vehicle_data.features,
        status=vehicle_data.status.value,
    )

    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)

    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update vehicle (manager and admin only).

    Args:
        vehicle_id: Vehicle ID
        vehicle_data: Updated vehicle data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated vehicle

    Raises:
        HTTPException: If vehicle not found, no permission, or chassis already exists
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission - non-admin can only edit vehicles from their dealership
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Check if chassis is being changed and if it's already in use
    if vehicle_data.chassis and vehicle_data.chassis != vehicle.chassis:
        result = await db.execute(
            select(Vehicle).where(
                and_(
                    Vehicle.chassis == vehicle_data.chassis,
                    Vehicle.deleted_at.is_(None),
                    Vehicle.id != vehicle_id
                )
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chassis already registered"
            )

    # Update fields
    if vehicle_data.title is not None:
        vehicle.title = vehicle_data.title
    if vehicle_data.description is not None:
        vehicle.description = vehicle_data.description
    if vehicle_data.brand is not None:
        vehicle.brand = vehicle_data.brand
    if vehicle_data.model is not None:
        vehicle.model = vehicle_data.model
    if vehicle_data.year is not None:
        vehicle.year = vehicle_data.year
    if vehicle_data.model_year is not None:
        vehicle.model_year = vehicle_data.model_year
    if vehicle_data.version is not None:
        vehicle.version = vehicle_data.version
    if vehicle_data.color is not None:
        vehicle.color = vehicle_data.color
    if vehicle_data.mileage is not None:
        vehicle.mileage = vehicle_data.mileage
    if vehicle_data.plate is not None:
        vehicle.plate = vehicle_data.plate
    if vehicle_data.chassis is not None:
        vehicle.chassis = vehicle_data.chassis
    if vehicle_data.doors is not None:
        vehicle.doors = vehicle_data.doors
    if vehicle_data.seats is not None:
        vehicle.seats = vehicle_data.seats
    if vehicle_data.fuel_type is not None:
        vehicle.fuel_type = vehicle_data.fuel_type.value
    if vehicle_data.transmission is not None:
        vehicle.transmission = vehicle_data.transmission.value
    if vehicle_data.body_type is not None:
        vehicle.body_type = vehicle_data.body_type.value
    if vehicle_data.price is not None:
        vehicle.price = vehicle_data.price
    if vehicle_data.video_url is not None:
        vehicle.video_url = str(vehicle_data.video_url)
    if vehicle_data.features is not None:
        vehicle.features = vehicle_data.features
    if vehicle_data.status is not None:
        vehicle.status = vehicle_data.status.value

    await db.commit()
    await db.refresh(vehicle)

    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete vehicle (soft delete, manager and admin only).

    Args:
        vehicle_id: Vehicle ID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If vehicle not found or no permission
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission - non-admin can only delete vehicles from their dealership
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Soft delete
    from datetime import datetime
    vehicle.deleted_at = datetime.utcnow()
    vehicle.status = VehicleStatus.INACTIVE

    await db.commit()


@router.post("/{vehicle_id}/analyze", response_model=VehicleAnalyzeResponse)
async def analyze_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze vehicle with AI (manager and admin only).

    Args:
        vehicle_id: Vehicle ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        AI analysis results

    Raises:
        HTTPException: If vehicle not found or no permission
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Perform AI analysis
    vehicle_data = {
        "id": str(vehicle.id),
        "price": float(vehicle.price),
        "year": vehicle.year,
        "mileage": vehicle.mileage or 0,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "body_type": vehicle.body_type,
        "fuel_type": vehicle.fuel_type,
        "features": vehicle.features or {},
        "ownership": vehicle.ownership,
        "description": vehicle.description,
        "title": vehicle.title,
    }

    # Use orchestrator if AI service is enabled
    from app.core.config import settings

    if settings.ENABLE_AI_SERVICE:
        orchestrator = get_orchestrator()
        analysis = await orchestrator.analyze_vehicle(vehicle_data, db)
    else:
        # Fallback to mock service
        analysis = await ai_service.analyze_vehicle(vehicle_data)

    # Update vehicle with analysis results
    vehicle.price_market = analysis["price_market"]
    vehicle.price_score = analysis["price_score"]
    vehicle.price_position = analysis["price_position"]
    vehicle.ai_analysis = analysis

    await db.commit()
    await db.refresh(vehicle)

    return VehicleAnalyzeResponse(
        price_market=analysis["price_market"],
        price_score=analysis["price_score"],
        price_position=analysis["price_position"],
        selling_points=analysis.get("selling_points", []),
        target_audience=analysis.get("target_audience", []),
        suggested_improvements=analysis.get("suggested_improvements", []),
        estimated_ctr=analysis.get("estimated_ctr", 0.0),
        estimated_conversion=analysis.get("estimated_conversion", 0.0),
        ai_analysis=analysis,
        analysis_version=analysis.get("analysis_version", "v1.0.0"),
        analyzed_at=analysis.get("analyzed_at", ""),
    )


@router.post("/{vehicle_id}/images", response_model=ImageUploadResponse)
async def upload_vehicle_images(
    vehicle_id: UUID,
    files: List[UploadFile] = File(...),
    set_main: bool = Query(False, description="Set first uploaded image as main"),
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload images for vehicle (manager and admin only).

    Args:
        vehicle_id: Vehicle ID
        files: List of image files
        set_main: Whether to set first image as main
        current_user: Current authenticated user
        db: Database session

    Returns:
        Uploaded image URLs

    Raises:
        HTTPException: If vehicle not found, no permission, or upload fails
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Check current image count
    current_count = len(vehicle.images) if vehicle.images else 0
    if current_count + len(files) > image_service.MAX_IMAGES_PER_VEHICLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {image_service.MAX_IMAGES_PER_VEHICLE} images per vehicle"
        )

    # Read files
    file_data = []
    for file in files:
        content = await file.read()
        file_data.append((content, file.filename, file.content_type))

    # Upload images
    uploaded_urls = await image_service.upload_images(file_data, str(vehicle_id))

    # Update vehicle images
    if vehicle.images is None:
        vehicle.images = []

    vehicle.images.extend(uploaded_urls)

    # Set main image if requested
    if set_main and uploaded_urls:
        vehicle.main_image = uploaded_urls[0]
    elif not vehicle.main_image and uploaded_urls:
        vehicle.main_image = uploaded_urls[0]

    await db.commit()
    await db.refresh(vehicle)

    return ImageUploadResponse(
        images=vehicle.images,
        main_image=vehicle.main_image,
    )


@router.get("/{vehicle_id}/similar", response_model=List[SimilarVehicleResponse])
async def get_similar_vehicles(
    vehicle_id: UUID,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get vehicles similar to a given vehicle.

    Uses semantic search with pgvector embeddings.

    Args:
        vehicle_id: Reference vehicle ID
        limit: Maximum number of results
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of similar vehicles with similarity scores

    Raises:
        HTTPException: If vehicle not found, no permission, or AI disabled
    """
    # Check if vector search is enabled
    from app.core.config import settings

    if not settings.ENABLE_VECTOR_SEARCH or not settings.ENABLE_AI_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector search is not enabled"
        )

    # Verify vehicle exists and user has permission
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get similar vehicles
    try:
        orchestrator = get_orchestrator()
        similar_vehicles = await orchestrator.find_similar_vehicles(
            db=db,
            vehicle_id=str(vehicle_id),
            limit=limit,
        )

        return similar_vehicles

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar vehicles: {str(e)}"
        )


@router.get("/search/semantic", response_model=List[SemanticSearchResponse])
async def semantic_search_vehicles(
    query: str = Query(..., min_length=3, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Semantic search for vehicles using natural language.

    Uses pgvector embeddings for intelligent search.

    Args:
        query: Search query text
        limit: Maximum number of results
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of matching vehicles with similarity scores

    Raises:
        HTTPException: If AI disabled
    """
    # Check if vector search is enabled
    from app.core.config import settings

    if not settings.ENABLE_VECTOR_SEARCH or not settings.ENABLE_AI_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Semantic search is not enabled"
        )

    # Build filters based on user role
    filters = {}
    if current_user.role != UserRole.ADMIN:
        # Non-admin users only see vehicles from their dealership
        # Note: This is applied in the query itself
        pass

    try:
        orchestrator = get_orchestrator()
        results = await orchestrator.search_vehicles_semantically(
            db=db,
            query_text=query,
            limit=limit,
            filters=filters,
        )

        # Filter results based on user permissions
        if current_user.role != UserRole.ADMIN:
            # Filter to only show vehicles from user's dealership
            results = [
                r for r in results
                if r.get("dealership_id") == str(current_user.dealership_id)
            ]

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/ai/generate-ad", response_model=Dict)
async def generate_vehicle_ad(
    vehicle_id: UUID,
    content_type: str = Query("full", description="Content type: 'headline' or 'full'"),
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate advertisement content for a vehicle.

    Uses AI to create compelling ad copy.

    Args:
        vehicle_id: Vehicle ID
        content_type: Type of content to generate
        current_user: Current authenticated user
        db: Database session

    Returns:
        Generated ad content

    Raises:
        HTTPException: If vehicle not found, no permission, or AI disabled
    """
    # Check if AI service is enabled
    from app.core.config import settings

    if not settings.ENABLE_AI_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not enabled"
        )

    # Get vehicle
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Prepare vehicle data
    vehicle_data = {
        "id": str(vehicle.id),
        "brand": vehicle.brand,
        "model": vehicle.model,
        "year": vehicle.year,
        "price": float(vehicle.price),
        "mileage": vehicle.mileage or 0,
        "body_type": vehicle.body_type,
        "transmission": vehicle.transmission,
        "fuel_type": vehicle.fuel_type,
        "features": vehicle.features or {},
        "description": vehicle.description,
        "title": vehicle.title,
        "version": vehicle.version,
        "color": vehicle.color,
    }

    try:
        orchestrator = get_orchestrator()
        ad_content = await orchestrator.generate_ad_content(
            vehicle_data=vehicle_data,
            content_type=content_type,
        )

        return ad_content

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ad content: {str(e)}"
        )



@router.delete("/{vehicle_id}/images/{image_index}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle_image(
    vehicle_id: UUID,
    image_index: int,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete image from vehicle (manager and admin only).

    Args:
        vehicle_id: Vehicle ID
        image_index: Index of image to delete
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If vehicle not found, no permission, or invalid index
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Validate index
    if not vehicle.images or image_index < 0 or image_index >= len(vehicle.images):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image index"
        )

    # Delete image from S3
    image_url = vehicle.images[image_index]
    await image_service.delete_image(image_url)

    # Remove from array
    vehicle.images.pop(image_index)

    # Update main_image if needed
    if vehicle.main_image == image_url:
        vehicle.main_image = vehicle.images[0] if vehicle.images else None

    await db.commit()


@router.patch("/{vehicle_id}/images/{image_index}/set-main", response_model=ImageUploadResponse)
async def set_main_vehicle_image(
    vehicle_id: UUID,
    image_index: int,
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Set main image for vehicle (manager and admin only).

    Args:
        vehicle_id: Vehicle ID
        image_index: Index of image to set as main
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated image URLs

    Raises:
        HTTPException: If vehicle not found, no permission, or invalid index
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Validate index
    if not vehicle.images or image_index < 0 or image_index >= len(vehicle.images):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image index"
        )

    # Set main image
    vehicle.main_image = vehicle.images[image_index]

    await db.commit()
    await db.refresh(vehicle)

    return ImageUploadResponse(
        images=vehicle.images,
        main_image=vehicle.main_image,
    )


@router.get("/{vehicle_id}/similar", response_model=List[SimilarVehicleResponse])
async def get_similar_vehicles(
    vehicle_id: UUID,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get vehicles similar to a given vehicle.

    Uses semantic search with pgvector embeddings.

    Args:
        vehicle_id: Reference vehicle ID
        limit: Maximum number of results
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of similar vehicles with similarity scores

    Raises:
        HTTPException: If vehicle not found, no permission, or AI disabled
    """
    # Check if vector search is enabled
    from app.core.config import settings

    if not settings.ENABLE_VECTOR_SEARCH or not settings.ENABLE_AI_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector search is not enabled"
        )

    # Verify vehicle exists and user has permission
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get similar vehicles
    try:
        orchestrator = get_orchestrator()
        similar_vehicles = await orchestrator.find_similar_vehicles(
            db=db,
            vehicle_id=str(vehicle_id),
            limit=limit,
        )

        return similar_vehicles

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar vehicles: {str(e)}"
        )


@router.get("/search/semantic", response_model=List[SemanticSearchResponse])
async def semantic_search_vehicles(
    query: str = Query(..., min_length=3, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Semantic search for vehicles using natural language.

    Uses pgvector embeddings for intelligent search.

    Args:
        query: Search query text
        limit: Maximum number of results
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of matching vehicles with similarity scores

    Raises:
        HTTPException: If AI disabled
    """
    # Check if vector search is enabled
    from app.core.config import settings

    if not settings.ENABLE_VECTOR_SEARCH or not settings.ENABLE_AI_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Semantic search is not enabled"
        )

    # Build filters based on user role
    filters = {}
    if current_user.role != UserRole.ADMIN:
        # Non-admin users only see vehicles from their dealership
        # Note: This is applied in the query itself
        pass

    try:
        orchestrator = get_orchestrator()
        results = await orchestrator.search_vehicles_semantically(
            db=db,
            query_text=query,
            limit=limit,
            filters=filters,
        )

        # Filter results based on user permissions
        if current_user.role != UserRole.ADMIN:
            # Filter to only show vehicles from user's dealership
            results = [
                r for r in results
                if r.get("dealership_id") == str(current_user.dealership_id)
            ]

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/ai/generate-ad", response_model=Dict)
async def generate_vehicle_ad(
    vehicle_id: UUID,
    content_type: str = Query("full", description="Content type: 'headline' or 'full'"),
    current_user: User = Depends(get_current_manager_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate advertisement content for a vehicle.

    Uses AI to create compelling ad copy.

    Args:
        vehicle_id: Vehicle ID
        content_type: Type of content to generate
        current_user: Current authenticated user
        db: Database session

    Returns:
        Generated ad content

    Raises:
        HTTPException: If vehicle not found, no permission, or AI disabled
    """
    # Check if AI service is enabled
    from app.core.config import settings

    if not settings.ENABLE_AI_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not enabled"
        )

    # Get vehicle
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id).where(Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Check permission
    if (current_user.role != UserRole.ADMIN and
        vehicle.dealership_id != current_user.dealership_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Prepare vehicle data
    vehicle_data = {
        "id": str(vehicle.id),
        "brand": vehicle.brand,
        "model": vehicle.model,
        "year": vehicle.year,
        "price": float(vehicle.price),
        "mileage": vehicle.mileage or 0,
        "body_type": vehicle.body_type,
        "transmission": vehicle.transmission,
        "fuel_type": vehicle.fuel_type,
        "features": vehicle.features or {},
        "description": vehicle.description,
        "title": vehicle.title,
        "version": vehicle.version,
        "color": vehicle.color,
    }

    try:
        orchestrator = get_orchestrator()
        ad_content = await orchestrator.generate_ad_content(
            vehicle_data=vehicle_data,
            content_type=content_type,
        )

        return ad_content

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ad content: {str(e)}"
        )

