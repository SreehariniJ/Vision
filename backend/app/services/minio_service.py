import io
import logging
from minio import Minio
from app.config import settings

logger = logging.getLogger(__name__)

class MinioService:
    """Service to interact with MinIO object storage."""
    
    def __init__(self):
        # We need to strip the http:// from MINIO_ENDPOINT if it exists
        endpoint = settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
        self.client = Minio(
            endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False # Internal Docker network
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to ensure MinIO bucket: {e}")

    def upload_file(self, object_name: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        """Uploads a file to MinIO and returns the storage path."""
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
            return f"{self.bucket_name}/{object_name}"
        except Exception as e:
            logger.error(f"MinIO upload failed: {e}")
            raise

    def get_file(self, object_name: str) -> bytes:
        """Retrieves a file from MinIO."""
        try:
            # Strip bucket name if it's passed in the path
            if object_name.startswith(f"{self.bucket_name}/"):
                object_name = object_name[len(self.bucket_name)+1:]
                
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        except Exception as e:
            logger.error(f"MinIO get failed: {e}")
            raise
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()

# Singleton instance
minio_service = MinioService()
