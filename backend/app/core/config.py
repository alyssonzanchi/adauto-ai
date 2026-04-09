"""
Application configuration using Pydantic Settings.
"""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/car_ads_db"
    )
    TEST_DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/car_ads_test"
    )

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = Field(default=3600)

    # JWT
    SECRET_KEY: str = Field(default="your-secret-key-change-this-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # AI APIs
    ANTHROPIC_API_KEY: str = Field(default="")
    OPENAI_API_KEY: str = Field(default="")

    # Facebook Ads
    FACEBOOK_APP_ID: str = Field(default="")
    FACEBOOK_APP_SECRET: str = Field(default="")
    FACEBOOK_API_VERSION: str = Field(default="v18.0")
    FACEBOOK_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/integrations/facebook/callback"
    )

    # Google Ads
    GOOGLE_ADS_DEVELOPER_TOKEN: str = Field(default="")
    GOOGLE_ADS_CLIENT_ID: str = Field(default="")
    GOOGLE_ADS_CLIENT_SECRET: str = Field(default="")
    GOOGLE_ADS_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/integrations/google/callback"
    )
    GOOGLE_ADS_API_VERSION: str = Field(default="v12")

    # S3 / MinIO
    AWS_ACCESS_KEY_ID: str = Field(default="minioadmin")
    AWS_SECRET_ACCESS_KEY: str = Field(default="minioadmin")
    AWS_S3_ENDPOINT: str = Field(default="http://localhost:9000")
    AWS_S3_BUCKET: str = Field(default="car-ads-images")
    AWS_REGION: str = Field(default="us-east-1")
    AWS_SIGNATURE_VERSION: str = Field(default="s3v4")

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")

    # Application
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    APP_NAME: str = Field(default="Car Ads Platform")
    APP_VERSION: str = Field(default="1.0.0")

    # CORS
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000")

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100)
    RATE_LIMIT_BURST: int = Field(default=200)

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20)
    MAX_PAGE_SIZE: int = Field(default=100)

    # File upload
    MAX_FILE_SIZE: int = Field(default=10485760)  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "webp"]
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")

    # Monitoring
    SENTRY_DSN: str = Field(default="")
    ENABLE_METRICS: bool = Field(default=True)

    # Feature flags
    ENABLE_AI_SERVICE: bool = Field(default=True)
    ENABLE_AUTO_OPTIMIZATION: bool = Field(default=False)
    ENABLE_ANALYTICS: bool = Field(default=True)


# Global settings instance
settings = Settings()
