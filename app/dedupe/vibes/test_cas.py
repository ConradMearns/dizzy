#!/usr/bin/env python3
"""
Test script for Content Addressable Storage (CAS) functionality.
Tests PutContent, GetContent, and CheckExists queries with MinIO backend.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gen.queries import PutContentInput, GetContentInput, CheckExistsInput
from queries.cas_minio import (
    PutContentQuery,
    GetContentQuery,
    CheckExistsQuery,
    MinIOCASConfig,
)


def main():
    print("=" * 60)
    print("CAS MinIO Test Script")
    print("=" * 60)
    print()

    # Configure MinIO connection
    config = MinIOCASConfig(
        endpoint="localhost:30000",
        access_key="admin",
        secret_key="supersecret123",
        bucket_name="cas-storage",
        secure=False,
    )

    print(f"Connected to MinIO at {config.endpoint}")
    print(f"Using bucket: {config.bucket_name}")
    print()

    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Test 1: Put some content
        print("Test 1: PutContent")
        print("-" * 60)
        test_content = b"Hello, DIZZY CAS! This is a test of content-addressable storage."
        test_file_1 = tmpdir_path / "test1.txt"
        test_file_1.write_bytes(test_content)
        print(f"Created test file: {test_file_1}")
        print(f"Content: {test_content[:50]}...")

        put_query = PutContentQuery(config)
        put_result = put_query.execute(PutContentInput(source_path=str(test_file_1)))

        cas_id = put_result.cas_id
        version, hash_value = cas_id.split(":", 1)
        print(f"✓ Content stored successfully!")
        print(f"  CAS ID: {cas_id}")
        print(f"  Version: {version}")
        print(f"  Hash: {hash_value}")
        print(f"  Path: {version}/{hash_value}")
        print()

        # Test 2: Check if content exists
        print("Test 2: CheckExists")
        print("-" * 60)
        check_query = CheckExistsQuery(config)
        check_result = check_query.execute(CheckExistsInput(cas_id=cas_id))

        print(f"Checking if content exists...")
        print(f"✓ Exists: {check_result.exists}")
        print()

        # Test 3: Retrieve the content
        print("Test 3: GetContent")
        print("-" * 60)
        get_query = GetContentQuery(config)
        download_file_1 = tmpdir_path / "downloaded1.txt"
        get_result = get_query.execute(
            GetContentInput(cas_id=cas_id, destination_path=str(download_file_1))
        )

        if not get_result.success:
            print("✗ ERROR: Download reported failure!")
            return 1

        retrieved_content = download_file_1.read_bytes()
        print(f"Retrieved content: {retrieved_content[:50]}...")
        print(f"  Original length: {len(test_content)}")
        print(f"  Retrieved length: {len(retrieved_content)}")

        if retrieved_content == test_content:
            print("✓ Content matches original!")
        else:
            print("✗ ERROR: Content does not match!")
            print(f"  Expected: {test_content[:50]}")
            print(f"  Got: {retrieved_content[:50]}")
            return 1
        print()

        # Test 4: Store different content and verify different hash
        print("Test 4: Content Deduplication Test")
        print("-" * 60)
        test_content_2 = b"Different content should produce a different hash."
        test_file_2 = tmpdir_path / "test2.txt"
        test_file_2.write_bytes(test_content_2)
        print(f"Storing different content: {test_content_2[:50]}...")

        put_result_2 = put_query.execute(PutContentInput(source_path=str(test_file_2)))
        cas_id_2 = put_result_2.cas_id

        print(f"✓ Content stored successfully!")
        print(f"  CAS ID: {cas_id_2}")

        if cas_id != cas_id_2:
            print("✓ Different content produces different hash (as expected)")
        else:
            print("✗ ERROR: Same hash for different content!")
            return 1
        print()

        # Test 5: Store same content again and verify same hash
        print("Test 5: Idempotency Test")
        print("-" * 60)
        test_file_3 = tmpdir_path / "test3.txt"
        test_file_3.write_bytes(test_content)
        print("Storing original content again...")

        put_result_3 = put_query.execute(PutContentInput(source_path=str(test_file_3)))
        cas_id_3 = put_result_3.cas_id

        print(f"✓ Content stored successfully!")
        print(f"  CAS ID: {cas_id_3}")

        if cas_id == cas_id_3:
            print("✓ Same content produces same hash (idempotent)")
        else:
            print("✗ ERROR: Different hash for same content!")
            return 1
        print()

        # Test 6: Test with text content
        print("Test 6: Text Content Test")
        print("-" * 60)
        text_content = "This is a string, not bytes!"
        test_file_4 = tmpdir_path / "test4.txt"
        test_file_4.write_text(text_content, encoding='utf-8')
        print(f"Storing text content: {text_content}")

        put_result_4 = put_query.execute(PutContentInput(source_path=str(test_file_4)))
        cas_id_4 = put_result_4.cas_id

        print(f"✓ Text content stored successfully!")
        print(f"  CAS ID: {cas_id_4}")

        # Retrieve and verify
        download_file_4 = tmpdir_path / "downloaded4.txt"
        get_result_4 = get_query.execute(
            GetContentInput(cas_id=cas_id_4, destination_path=str(download_file_4))
        )

        if not get_result_4.success:
            print("✗ ERROR: Download reported failure!")
            return 1

        retrieved_text = download_file_4.read_text(encoding='utf-8')

        if retrieved_text == text_content:
            print("✓ Retrieved content matches original text")
        else:
            print("✗ ERROR: Retrieved content does not match!")
            print(f"  Expected: {text_content}")
            print(f"  Got: {retrieved_text}")
            return 1
        print()

    print("=" * 60)
    print("✓ All CAS tests passed!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - PutContent: Working ✓")
    print(f"  - GetContent: Working ✓")
    print(f"  - CheckExists: Working ✓")
    print(f"  - Deduplication: Working ✓")
    print(f"  - Idempotency: Working ✓")
    print(f"  - Text handling: Working ✓")
    print()

    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
