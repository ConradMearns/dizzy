#!/usr/bin/env python3
"""
Test script for CAS (Content Addressable Storage) with path-based interface.
Upload an image file and retrieve it using the new path-based CAS queries.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from queries.cas_minio import (
    PutContentQuery,
    GetContentQuery,
    CheckExistsQuery,
    MinIOCASConfig,
)
from gen.queries import (
    PutContentInput,
    GetContentInput,
    CheckExistsInput,
)


def main():
    # MinIO connection config (from PULUMI.md)
    config = MinIOCASConfig(
        endpoint="localhost:30000",
        access_key="admin",
        secret_key="supersecret123",
        bucket_name="cas-storage",
        secure=False,
    )

    # Initialize queries
    put_query = PutContentQuery(config)
    get_query = GetContentQuery(config)
    check_query = CheckExistsQuery(config)

    # Test file: use example image
    source_file = Path(__file__).parent.parent / "examples" / "01.jpg"
    download_file = Path(__file__).parent / "downloaded_01.jpg"

    print(f"=== CAS Path-Based Upload/Download Test ===\n")
    print(f"Source file: {source_file}")
    print(f"Download destination: {download_file}\n")

    # Step 1: Upload the image
    print("Step 1: Uploading image to CAS...")
    try:
        put_result = put_query.execute(PutContentInput(source_path=str(source_file)))
        cas_id = put_result.cas_id
        print(f"✓ Upload successful!")
        print(f"  CAS ID: {cas_id}\n")
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return 1

    # Step 2: Check if content exists
    print("Step 2: Checking if content exists in CAS...")
    try:
        check_result = check_query.execute(CheckExistsInput(cas_id=cas_id))
        if check_result.exists:
            print(f"✓ Content exists in CAS\n")
        else:
            print(f"✗ Content not found in CAS\n")
            return 1
    except Exception as e:
        print(f"✗ Check failed: {e}")
        return 1

    # Step 3: Download the content
    print("Step 3: Downloading content from CAS...")
    try:
        # Clean up any existing download file
        if download_file.exists():
            download_file.unlink()

        get_result = get_query.execute(
            GetContentInput(cas_id=cas_id, destination_path=str(download_file))
        )
        if get_result.success:
            print(f"✓ Download successful!")
            print(f"  Downloaded to: {download_file}")
            print(f"  File size: {download_file.stat().st_size} bytes\n")
        else:
            print(f"✗ Download reported failure\n")
            return 1
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return 1

    # Step 4: Verify file integrity
    print("Step 4: Verifying file integrity...")
    source_size = source_file.stat().st_size
    download_size = download_file.stat().st_size

    if source_size == download_size:
        print(f"✓ File sizes match: {source_size} bytes")

        # Also verify content is identical
        with open(source_file, 'rb') as f1, open(download_file, 'rb') as f2:
            if f1.read() == f2.read():
                print(f"✓ File contents match - integrity verified!\n")
            else:
                print(f"✗ File contents differ\n")
                return 1
    else:
        print(f"✗ File sizes differ: {source_size} vs {download_size}\n")
        return 1

    print("=== All tests passed! ===")
    return 0


if __name__ == "__main__":
    exit(main())
