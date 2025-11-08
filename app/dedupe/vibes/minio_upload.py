#!/usr/bin/env python3
"""
Simple MinIO upload script.
Upload a file and get a presigned URL to access it.
"""

from minio import Minio
from datetime import timedelta

# MinIO connection details (from PULUMI.md)
MINIO_ENDPOINT = "localhost:30000"
MINIO_USER = "admin"
MINIO_PASSWORD = "supersecret123"
BUCKET_NAME = "test-bucket"

def main():
    # Initialize MinIO client
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_USER,
        secret_key=MINIO_PASSWORD,
        secure=False  # Set to True if using HTTPS
    )

    print(f"Connected to MinIO at {MINIO_ENDPOINT}")

    # Create bucket if it doesn't exist
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
        print(f"Created bucket: {BUCKET_NAME}")
    else:
        print(f"Bucket already exists: {BUCKET_NAME}")

    # Upload a test file
    file_to_upload = "README.md"  # Change this to your file
    object_name = "uploaded_readme.md"  # Name in MinIO

    try:
        client.fput_object(
            BUCKET_NAME,
            object_name,
            file_to_upload,
        )
        print(f"\nUploaded {file_to_upload} as {object_name}")

        # Get presigned URL (valid for 7 days)
        url = client.presigned_get_object(
            BUCKET_NAME,
            object_name,
            expires=timedelta(days=7)
        )
        print(f"\nAccess URL (valid for 7 days):")
        print(url)

        # Also show direct access method
        print(f"\nDirect access (requires auth):")
        print(f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{object_name}")

        # List all objects in bucket
        print(f"\nAll objects in {BUCKET_NAME}:")
        objects = client.list_objects(BUCKET_NAME)
        for obj in objects:
            print(f"  - {obj.object_name} ({obj.size} bytes)")

    except Exception as e:
        print(f"Error uploading file: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
