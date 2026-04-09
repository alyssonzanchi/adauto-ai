"""
API dependencies.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models import User, UserRole
from app.models.enums import UserStatus


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")

    if user_id is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        Active user

    Raises:
        HTTPException: If user is not active
    """
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current admin user.

    Args:
        current_user: Current user from token

    Returns:
        Admin user

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_manager_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current manager or admin user.

    Args:
        current_user: Current user from token

    Returns:
        Manager or admin user

    Raises:
        HTTPException: If user is not manager or admin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


class RequirePermission:
    """
    Dependency to check if user has specific permission.

    Usage:
        @app.get("/vehicles")
        async def get_vehicles(
            _: None = Depends(RequirePermission("vehicles:view"))
        ):
            ...
    """

    def __init__(self, permission: str):
        """
        Initialize permission requirement.

        Args:
            permission: Required permission
        """
        self.permission = permission

    def __call__(
        self,
        current_user: User = Depends(get_current_user)
    ) -> None:
        """
        Check if user has permission.

        Args:
            current_user: Current user

        Raises:
            HTTPException: If user doesn't have permission
        """
        if current_user.role == UserRole.ADMIN:
            return

        if self.permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{self.permission}' required"
            )
