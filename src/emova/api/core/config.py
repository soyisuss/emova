"""
Environment Configuration Module (Settings) using Pydantic.

Centralizes the extraction of secrets and credentials using a `.env` file
backporting security risks according to standards (not uploaded to Source Control).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main class that injects dependencies to the global settings object."""
    PROJECT_NAME: str = "EMOVA API"
    MONGODB_URL: str = "mongodb://localhost:27017"  # Overridden from .env
    DATABASE_NAME: str = "emova_db"

    # Sensitive Cryptographic Security Parameters
    SECRET_KEY: str = "super_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # SMTP Configuration
    SMTP_SERVER: str | None = None
    SMTP_PORT: int | None = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None

    # Google Cloud Storage Settings
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    GCP_PROJECT_ID: str | None = None
    GCS_BUCKET_NAME: str | None = None

    # The extra="ignore" flag discards variables defined in an extra runtime not specified above.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
