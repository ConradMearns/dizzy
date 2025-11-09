#!/usr/bin/env python3

"""
FileItemScanned policy implementation.

This policy appends file metadata to partition-specific manifest CSVs
when files are scanned during partition processing.
"""

from policies.interfaces import FileItemScannedPolicyProtocol
from gen.policies import FileItemScannedPolicyContext
from gen.events import FileItemScanned
from gen.mutations import AppendToManifestInput


class FileItemScannedPolicy:
    """Append scanned file metadata to partition manifest CSV."""

    def __call__(self, context: FileItemScannedPolicyContext, event: FileItemScanned) -> None:
        """
        Execute the FileItemScanned policy.

        This policy:
        1. Extracts file metadata from the event
        2. Calls the append_to_manifest mutator to write to CSV
        3. Logs the result
        """
        print(f"\n📝 Adding file to manifest:")
        print(f"   Partition: {event.partition_uuid}")
        print(f"   Path: {event.path}")
        print(f"   CAS ID: {event.cas_id}")
        print(f"   Hash: {event.content_hash}")
        print(f"   Size: {event.size} bytes")

        # Create the mutation input
        manifest_input = AppendToManifestInput(
            partition_uuid=event.partition_uuid,
            path=event.path,
            cas_id=event.cas_id,
            content_hash=event.content_hash,
            size=event.size
        )

        # Execute the append mutation
        result = context.mutate.append_to_manifest(manifest_input)

        if result.success:
            print(f"   ✓ Successfully appended to {result.manifest_path}")
        else:
            print(f"   ✗ Failed to append: {result.error_message}")

        print()
