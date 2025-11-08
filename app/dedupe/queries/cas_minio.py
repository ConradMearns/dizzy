"""
MinIO-based implementation for Content Addressable Storage queries.

HIDDEN DEPENDENCIES:
- Network: MinIO server must be accessible
- Config: MinIO credentials must be configured

CAS Identity Format:
- String format: "version:hash" (e.g., "DZ0:5Z7uzFjrU6xn1NDhYByYaTDeT")
- Stored in MinIO as: {version}/{hash}
"""

import blake3
import base58
from minio import Minio
from io import BytesIO

from gen.queries import (
    PutContentInput,
    PutContent,
    GetContentInput,
    GetContent,
    CheckExistsInput,
    CheckExists,
)


class MinIOCASConfig:
    """Configuration for MinIO CAS storage."""

    def __init__(
        self,
        endpoint: str = "localhost:30000",
        access_key: str = "admin",
        secret_key: str = "supersecret123",
        bucket_name: str = "cas-storage",
        secure: bool = False,
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.secure = secure


class PutContentQuery:
    """Store content in MinIO using content-addressing."""

    def __init__(self, config: MinIOCASConfig | None = None):
        self.config = config or MinIOCASConfig()
        self.client = Minio(
            self.config.endpoint,
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
            secure=self.config.secure,
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        if not self.client.bucket_exists(self.config.bucket_name):
            self.client.make_bucket(self.config.bucket_name)

    def execute(self, query_input: PutContentInput) -> PutContent:
        # Convert content to bytes if needed
        content_bytes = query_input.content
        if isinstance(content_bytes, str):
            content_bytes = content_bytes.encode('utf-8')

        # Compute BLAKE3 hash
        hasher = blake3.blake3()
        hasher.update(content_bytes)
        hash_bytes = hasher.digest()

        # Encode as base58
        hash_b58 = base58.b58encode(hash_bytes).decode('ascii')

        # Create CAS identity string in format "version:hash"
        version = "DZ0"
        cas_id_str = f"{version}:{hash_b58}"

        # Store in MinIO at /version/hash
        object_path = f"{version}/{hash_b58}"

        # Upload content
        content_stream = BytesIO(content_bytes)
        self.client.put_object(
            self.config.bucket_name,
            object_path,
            content_stream,
            length=len(content_bytes),
        )

        return PutContent(cas_id=cas_id_str)


class GetContentQuery:
    """Retrieve content from MinIO by CAS identity."""

    def __init__(self, config: MinIOCASConfig | None = None):
        self.config = config or MinIOCASConfig()
        self.client = Minio(
            self.config.endpoint,
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
            secure=self.config.secure,
        )

    def execute(self, query_input: GetContentInput) -> GetContent:
        # Parse CAS ID string "version:hash"
        cas_id_str = query_input.cas_id
        version, hash_b58 = cas_id_str.split(":", 1)
        object_path = f"{version}/{hash_b58}"

        # Retrieve from MinIO
        response = self.client.get_object(
            self.config.bucket_name,
            object_path,
        )

        # Read all content
        content_bytes = response.read()
        response.close()
        response.release_conn()

        return GetContent(content=content_bytes)


class CheckExistsQuery:
    """Check if content exists in MinIO by CAS identity."""

    def __init__(self, config: MinIOCASConfig | None = None):
        self.config = config or MinIOCASConfig()
        self.client = Minio(
            self.config.endpoint,
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
            secure=self.config.secure,
        )

    def execute(self, query_input: CheckExistsInput) -> CheckExists:
        # Parse CAS ID string "version:hash"
        cas_id_str = query_input.cas_id
        version, hash_b58 = cas_id_str.split(":", 1)
        object_path = f"{version}/{hash_b58}"

        try:
            # Try to get object metadata (stat_object is more efficient than get_object)
            self.client.stat_object(
                self.config.bucket_name,
                object_path,
            )
            exists = True
        except Exception:
            exists = False

        return CheckExists(exists=exists)
