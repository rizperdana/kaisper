"""S3-compatible storage client for Kaisper."""

import os
from typing import Any, Dict, List, Optional
from loguru import logger

try:
    import boto3
    from botocore.client import Config
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not available, S3 storage will be disabled")


class S3Storage:
    """S3-compatible storage client."""
    
    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket: Optional[str] = None,
        region: str = "us-east-1",
    ):
        """Initialize S3 storage client."""
        if not BOTO3_AVAILABLE:
            logger.warning("S3 storage not available (boto3 not installed)")
            self.client = None
            return
        
        self.endpoint_url = endpoint_url or os.getenv("KAISPER_S3_ENDPOINT_URL")
        self.access_key = access_key or os.getenv("KAISPER_S3_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("KAISPER_S3_SECRET_KEY")
        self.bucket = bucket or os.getenv("KAISPER_S3_BUCKET")
        self.region = region
        
        if not all([self.endpoint_url, self.access_key, self.secret_key, self.bucket]):
            logger.warning("S3 configuration incomplete, storage will be disabled")
            self.client = None
            return
        
        try:
            self.client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                config=Config(signature_version='s3v4'),
            )
            logger.info("S3 storage client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.client = None
    
    def upload_file(
        self,
        file_path: str,
        object_key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Upload a file to S3."""
        if not self.client:
            logger.warning("S3 client not available")
            return False
        
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata
            
            self.client.upload_file(
                file_path,
                self.bucket,
                object_key,
                ExtraArgs=extra_args,
            )
            logger.info(f"Uploaded {file_path} to s3://{self.bucket}/{object_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {file_path}: {e}")
            return False
    
    def download_file(
        self,
        object_key: str,
        file_path: str,
    ) -> bool:
        """Download a file from S3."""
        if not self.client:
            logger.warning("S3 client not available")
            return False
        
        try:
            self.client.download_file(
                self.bucket,
                object_key,
                file_path,
            )
            logger.info(f"Downloaded s3://{self.bucket}/{object_key} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {object_key}: {e}")
            return False
    
    def delete_file(self, object_key: str) -> bool:
        """Delete a file from S3."""
        if not self.client:
            logger.warning("S3 client not available")
            return False
        
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=object_key,
            )
            logger.info(f"Deleted s3://{self.bucket}/{object_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {object_key}: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in S3 bucket."""
        if not self.client:
            logger.warning("S3 client not available")
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
            )
            
            files = []
            if "Contents" in response:
                files = [obj["Key"] for obj in response["Contents"]]
            
            logger.info(f"Listed {len(files)} files with prefix {prefix}")
            return files
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def file_exists(self, object_key: str) -> bool:
        """Check if a file exists in S3."""
        if not self.client:
            logger.warning("S3 client not available")
            return False
        
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=object_key,
            )
            return True
        except Exception:
            return False
    
    def get_file_metadata(self, object_key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a file."""
        if not self.client:
            logger.warning("S3 client not available")
            return None
        
        try:
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=object_key,
            )
            
            metadata = {
                "size": response.get("ContentLength", 0),
                "last_modified": response.get("LastModified"),
                "content_type": response.get("ContentType"),
                "metadata": response.get("Metadata", {}),
            }
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to get metadata for {object_key}: {e}")
            return None


# Global S3 storage instance
s3_storage = S3Storage()
