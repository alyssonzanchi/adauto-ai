"""
Pagination schemas.
"""
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema for paginated response."""

    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    class Config:
        """Pydantic config."""

        from_attributes = True


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

    @property
    def skip(self) -> int:
        """Calculate offset."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit."""
        return self.page_size
