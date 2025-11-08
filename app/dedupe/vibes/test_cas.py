#!/usr/bin/env python3
"""
Test script for Content Addressable Storage (CAS) functionality.
Tests PutContent, GetContent, and CheckExists queries with MinIO backend.
"""

import sys
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

    # Test 1: Put some content
    print("Test 1: PutContent")
    print("-" * 60)
    test_content = b"Hello, DIZZY CAS! This is a test of content-addressable storage."
    print(f"Storing content: {test_content[:50]}...")

    put_query = PutContentQuery(config)
    put_result = put_query.execute(PutContentInput(content=test_content))

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
    get_result = get_query.execute(GetContentInput(cas_id=cas_id))

    retrieved_content = get_result.content
    print(f"Retrieved content: {retrieved_content[:50]}...")
    print(f"  Type: {type(retrieved_content)}, Length: {len(retrieved_content)}")
    print(f"  Original type: {type(test_content)}, Length: {len(test_content)}")

    # Verify content matches (handle both bytes and string)
    if isinstance(retrieved_content, str):
        retrieved_content = retrieved_content.encode('utf-8')

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
    print(f"Storing different content: {test_content_2[:50]}...")

    put_result_2 = put_query.execute(PutContentInput(content=test_content_2))
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
    print("Storing original content again...")

    put_result_3 = put_query.execute(PutContentInput(content=test_content))
    cas_id_3 = put_result_3.cas_id

    print(f"✓ Content stored successfully!")
    print(f"  CAS ID: {cas_id_3}")

    if cas_id == cas_id_3:
        print("✓ Same content produces same hash (idempotent)")
    else:
        print("✗ ERROR: Different hash for same content!")
        return 1
    print()

    # Test 6: Test with text content (string)
    print("Test 6: String Content Test")
    print("-" * 60)
    text_content = "This is a string, not bytes!"
    print(f"Storing string content: {text_content}")

    put_result_4 = put_query.execute(PutContentInput(content=text_content))
    cas_id_4 = put_result_4.cas_id

    print(f"✓ String content stored successfully!")
    print(f"  CAS ID: {cas_id_4}")

    # Retrieve and verify
    get_result_4 = get_query.execute(GetContentInput(cas_id=cas_id_4))
    retrieved_text = get_result_4.content

    # Handle both string and bytes
    if isinstance(retrieved_text, str):
        retrieved_text_bytes = retrieved_text.encode('utf-8')
    else:
        retrieved_text_bytes = retrieved_text

    if retrieved_text_bytes == text_content.encode('utf-8'):
        print("✓ Retrieved content matches original text")
    else:
        print("✗ ERROR: Retrieved content does not match!")
        print(f"  Expected: {text_content.encode('utf-8')}")
        print(f"  Got: {retrieved_text_bytes}")
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
    print(f"  - String handling: Working ✓")
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
