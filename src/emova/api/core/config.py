"""
Módulo de configuración del entorno (ajustes) mediante Pydantic.

Centraliza la extracción de secretos y credenciales utilizando un archivo `.env`
para evitar riesgos de seguridad de acuerdo con los estándares (no se sube al control de versiones).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Clase principal que inyecta dependencias al objeto de configuración global."""
    PROJECT_NAME: str = "EMOVA API"
    MONGODB_URL: str = "mongodb://localhost:27017"  # Sobrescribible desde .env
    DATABASE_NAME: str = "emova_db"

    # Parámetros criptográficos sensibles de seguridad
    SECRET_KEY: str = "super_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días

    # Configuración de SMTP
    SMTP_SERVER: str | None = None
    SMTP_PORT: int | None = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None

    # Configuración de Google Cloud Storage
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    GCP_PROJECT_ID: str | None = None
    GCS_BUCKET_NAME: str | None = None

    # La bandera extra="ignore" descarta variables definidas en el .env que no estén declaradas aquí
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

