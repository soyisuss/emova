"""
Módulo de integración con Google Cloud Storage.

Maneja subidas seguras de reportes directamente a los buckets de GCP.
"""
import asyncio
import logging
from google.cloud import storage

from emova.api.core.config import settings

logger = logging.getLogger(__name__)

class StorageManager:
    """Administra la conexión y las acciones sobre el Bucket de Google Cloud configurado."""
    _client = None
    
    @classmethod
    def get_client(cls):
        """Patrón Singleton para inicializar el cliente de almacenamiento una sola vez."""
        if cls._client is None:
            try:
                if settings.GOOGLE_APPLICATION_CREDENTIALS:
                    # Uso local: cargar desde el archivo JSON si existe la variable
                    cls._client = storage.Client.from_service_account_json(
                        json_credentials_path=settings.GOOGLE_APPLICATION_CREDENTIALS,
                        project=settings.GCP_PROJECT_ID
                    )
                else:
                    # Uso en Producción (Cloud Run): Autenticación nativa e invisible de GCP
                    cls._client = storage.Client(project=settings.GCP_PROJECT_ID)
            except Exception as e:
                logger.error(f"Error initializing Google Cloud Storage client: {e}")
        return cls._client
        
    @classmethod
    def _upload_sync(cls, file_bytes: bytes, user_id: str, filename: str) -> str:
        """Envoltura síncrona para subir archivos (blobs)."""
        client = cls.get_client()
        if not client:
            raise RuntimeError("Google Cloud Storage client is not initialized. Please verify your credentials and .env configuration.")
            
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        
        # Almacenamos los archivos aislados por user_id
        blob_path = f"reports/{user_id}/{filename}"
        blob = bucket.blob(blob_path)
        
        # Ejecutar la transferencia de red
        blob.upload_from_string(file_bytes, content_type="application/pdf")
        
        # Retornamos la URL de descarga directa en la API del almacenamiento
        url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{blob_path}"
        logger.info(f"Report PDF successfully uploaded to GCS: {url}")
        return url

    @classmethod
    async def upload_report_pdf(cls, file_bytes: bytes, user_id: str, filename: str) -> str:
        """
        Sube asíncronamente un reporte PDF a Google Cloud Storage.
        Delega la llamada síncrona bloqueante del SDK a un hilo de trabajo.
        """
        return await asyncio.to_thread(cls._upload_sync, file_bytes, user_id, filename)

    @classmethod
    def _download_sync(cls, raw_db_url: str) -> bytes:
        """Descarga de forma síncrona un archivo en bytes crudos analizando su URI original."""
        client = cls.get_client()
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        
        prefix = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/"
        blob_path = raw_db_url.replace(prefix, "")
        
        blob = bucket.blob(blob_path)
        return blob.download_as_bytes()

    @classmethod
    async def download_report_pdf(cls, raw_db_url: str) -> bytes:
        """
        Descarga asíncronamente un PDF de forma segura sin exponer endpoints de GCS directamente.
        """
        return await asyncio.to_thread(cls._download_sync, raw_db_url)
