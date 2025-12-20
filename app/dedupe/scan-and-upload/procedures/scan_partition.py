#!/usr/bin/env python3

"""
ScanPartition procedure implementation.
"""

import hashlib
from pathlib import Path

from procedures.interfaces import ScanPartitionProcedureProtocol
from gen.procedures import ScanPartitionContext
from gen.commands import ScanPartition
from gen.queries import ListFileItemsInput, PutContentInput
from gen.events import FileItemScanned, FileItemProblem


class ScanPartitionProcedure:
    """Scan a partition and emit FileItemScanned events for each file."""

    def __call__(self, context: ScanPartitionContext, command: ScanPartition) -> None:
        # Get all file items in the partition
        file_items = context.query.list_file_items(
            ListFileItemsInput(partition_uuid=command.partition_uuid)
        )

        # Scan each file
        for file_path_str in file_items.file_items:
            file_path = Path(file_path_str)

            if not file_path.exists() or not file_path.is_file():
                continue

            try:
                # Compute hash for tracking purposes
                hasher = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        hasher.update(chunk)

                # Store content in CAS using path-based interface
                put_result = context.query.put_content(
                    PutContentInput(source_path=str(file_path))
                )

                # Emit event with CAS ID
                context.emit.scanned(FileItemScanned(
                    partition_uuid=command.partition_uuid,
                    path=str(file_path),
                    size=file_path.stat().st_size,
                    content_hash=hasher.hexdigest(),
                    cas_id=put_result.cas_id
                ))
                print(file_path, put_result.cas_id)
            except Exception as e:
                # Emit problem event and continue with next file
                error_msg = f"{type(e).__name__}: {str(e)}"
                context.emit.problem(FileItemProblem(
                    partition_uuid=command.partition_uuid,
                    path=str(file_path),
                    error=error_msg
                ))
                print(f"ERROR: {file_path} - {error_msg}")

# Type check: Ensure we implement the protocol correctly
_: ScanPartitionProcedureProtocol = ScanPartitionProcedure()
