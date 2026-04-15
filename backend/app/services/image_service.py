"""
Image upload service for MinIO/S3.
"""
import uuid
from io import BytesIO
from typing import List, Tuple, Optional

import boto3
from botocore.exceptions import ClientError
from PIL import Image
from fastapi import HTTPException, status

from app.core.config import settings


class ImageService:
    """Service for handling image uploads to MinIO/S3."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGES_PER_VEHICLE = 20
    MAX_IMAGE_WIDTH = 1200
    JPEG_QUALITY = 85

    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
    ALLOWED_MIME_TYPES = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    def __init__(self):
        """Initialize S3 client."""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.AWS_S3_BUCKET

    async def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket)
                except ClientError as create_error:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create bucket: {str(create_error)}"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"S3 error: {str(e)}"
                )

    def _validate_image(
        self,
        file_content: bytes,
        filename: str,
        content_type: str
    ) -> None:
        """
        Validate image file.

        Args:
            file_content: File content bytes
            filename: Original filename
            content_type: MIME type

        Raises:
            HTTPException: If validation fails
        """
        # Check file size
        if len(file_content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds {self.MAX_FILE_SIZE // (1024*1024)}MB limit"
            )

        # Check MIME type
        if content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )

        # Check file extension
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # Try to open with PIL to verify it's a valid image
        try:
            img = Image.open(BytesIO(file_content))
            img.verify()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )

    def _process_image(self, file_content: bytes) -> bytes:
        """
        Process image: resize if needed and convert to JPEG.

        Args:
            file_content: Original file content

        Returns:
            Processed image bytes
        """
        try:
            img = Image.open(BytesIO(file_content))

            # Convert RGBA to RGB
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if too large
            if img.width > self.MAX_IMAGE_WIDTH:
                ratio = self.MAX_IMAGE_WIDTH / img.width
                new_height = int(img.height * ratio)
                img = img.resize((self.MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)

            # Save as JPEG
            output = BytesIO()
            img.save(output, format="JPEG", quality=self.JPEG_QUALITY, optimize=True)
            return output.getvalue()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process image: {str(e)}"
            )

    async def upload_images(
        self,
        files: List[Tuple[bytes, str, str]],
        vehicle_id: str
    ) -> List[str]:
        """
        Upload multiple images for a vehicle.

        Args:
            files: List of (content, filename, content_type) tuples
            vehicle_id: Vehicle UUID

        Returns:
            List of uploaded image URLs

        Raises:
            HTTPException: If upload fails or too many images
        """
        await self._ensure_bucket_exists()

        if len(files) > self.MAX_IMAGES_PER_VEHICLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {self.MAX_IMAGES_PER_VEHICLE} images per vehicle"
            )

        uploaded_urls = []

        for file_content, filename, content_type in files:
            # Validate
            self._validate_image(file_content, filename, content_type)

            # Process
            processed_content = self._process_image(file_content)

            # Generate unique filename
            ext = "jpg"
            unique_filename = f"vehicles/{vehicle_id}/{uuid.uuid4()}.{ext}"

            # Upload to S3
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=unique_filename,
                    Body=processed_content,
                    ContentType="image/jpeg",
                )

                # Generate public URL
                url = f"{settings.AWS_S3_ENDPOINT}/{self.bucket}/{unique_filename}"
                uploaded_urls.append(url)

            except ClientError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {str(e)}"
                )

        return uploaded_urls

    async def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from S3.

        Args:
            image_url: Full URL of the image

        Returns:
            True if deleted successfully

        Raises:
            HTTPException: If deletion fails
        """
        try:
            # Extract key from URL
            # URL format: http://localhost:9000/bucket/key
            parts = image_url.split(f"/{self.bucket}/", 1)
            if len(parts) != 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image URL"
                )

            key = parts[1]

            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=key
            )

            return True

        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete image: {str(e)}"
            )

    async def delete_vehicle_images(self, vehicle_id: str) -> None:
        """
        Delete all images for a vehicle.

        Args:
            vehicle_id: Vehicle UUID
        """
        try:
            # List all objects with the vehicle prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=f"vehicles/{vehicle_id}/"
            )

            if "Contents" in response:
                # Delete all objects
                for obj in response["Contents"]:
                    self.s3_client.delete_object(
                        Bucket=self.bucket,
                        Key=obj["Key"]
                    )

        except ClientError:
            # Don't raise if deletion fails - vehicle deletion should continue
            pass

    def get_public_url(self, key: str) -> str:
        """
        Generate public URL for an image.

        Args:
            key: S3 object key

        Returns:
            Public URL
        """
        return f"{settings.AWS_S3_ENDPOINT}/{self.bucket}/{key}"


# Global image service instance
image_service = ImageService()
