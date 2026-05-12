"""
Google Cloud Storage Integration Module.

Handles secure uploads of user-related content directly to GCP
buckets using the asyncio bridge.
"""
import asyncio
import logging
from google.cloud import storage

from emova.api.core.config import settings

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages the connection and actions upon the configured Google Cloud Bucket."""
    _client = None
    
    @classmethod
    def get_client(cls):
        """Singleton pattern for initializing the Storage client only once."""
        if cls._client is None:
            if settings.GCS_BUCKET_NAME and settings.GOOGLE_APPLICATION_CREDENTIALS:
                try:
                    # Explicitly pass the path from Settings as Python environment variables might not carry it implicitly
                    cls._client = storage.Client.from_service_account_json(
                        json_credentials_path=settings.GOOGLE_APPLICATION_CREDENTIALS,
                        project=settings.GCP_PROJECT_ID
                    )
                except Exception as e:
                    logger.error(f"Error initializing Google Cloud Storage client: {e}")
            elif settings.GCS_BUCKET_NAME:
                try:
                    # Fallback to default credentials (ideal for Cloud Run)
                    cls._client = storage.Client(project=settings.GCP_PROJECT_ID)
                except Exception as e:
                    logger.error(f"Error initializing default GCS client: {e}")
        return cls._client
        
    @classmethod
    def _upload_sync(cls, file_bytes: bytes, user_id: str, filename: str) -> str:
        """Synchronous wrapper for uploading blobs."""
        client = cls.get_client()
        if not client:
            raise RuntimeError("Google Cloud Storage client is not initialized. Please verify your credentials and .env configuration.")
            
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        
        # We store files isolated by user_id
        blob_path = f"reports/{user_id}/{filename}"
        blob = bucket.blob(blob_path)
        
        # Execute the network transfer
        blob.upload_from_string(file_bytes, content_type="application/pdf")
        
        # We return the direct storage API URL (Assuming the UI or Mobile app parses it to download)
        url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{blob_path}"
        logger.info(f"Report PDF successfully uploaded to GCS: {url}")
        return url

    @classmethod
    async def upload_report_pdf(cls, file_bytes: bytes, user_id: str, filename: str) -> str:
        """
        Asynchronously upload a PDF report to Google Cloud Storage.
        Offloads the heavy IO blocking synchronous SDK call to a worker thread.
        """
        return await asyncio.to_thread(cls._upload_sync, file_bytes, user_id, filename)

    @classmethod
    def _download_sync(cls, raw_db_url: str) -> bytes:
        """Synchronously downloads a blob as direct raw bytes parsing its original URI."""
        client = cls.get_client()
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        
        prefix = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/"
        blob_path = raw_db_url.replace(prefix, "")
        
        blob = bucket.blob(blob_path)
        return blob.download_as_bytes()

    @classmethod
    async def download_report_pdf(cls, raw_db_url: str) -> bytes:
        """
        Asynchronously downloads a PDF securely without exposing GCS endpoints directly.
        """
        return await asyncio.to_thread(cls._download_sync, raw_db_url)
