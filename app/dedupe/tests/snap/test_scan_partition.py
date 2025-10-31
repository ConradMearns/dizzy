import pytest
from gen.commands import ScanPartition
from gen.procedures import ScanPartitionContext, ScanPartitionEmitters, ScanPartitionQueries
from gen.events import FileItemScanned
from procedures.scan_partition import ScanPartitionProcedure
from queries.file_scanners.linux import ListHardDrivesQuery, ListPartitionsQuery, ListFileItemsQuery


@pytest.mark.manual
def test_scan_partition():
    """Manual test for ScanPartition procedure.

    Run with: uv run pytest tests/snap/test_scan_partition.py -m manual -s
    """
    print("\n" + "="*60)
    print("Starting ScanPartition Manual Test")
    print("="*60)

    # Emit function to capture scanned events
    def emit_scanned(event: FileItemScanned) -> None:
        print(f"  [EVENT] FileItemScanned:")
        print(f"    - partition: {event.partition_uuid}")
        print(f"    - path: {event.path}")
        print(f"    - size: {event.size} bytes")
        print(f"    - hash: {event.content_hash}")

    # Instantiate query implementations
    list_hard_drives_query = ListHardDrivesQuery()
    list_partitions_query = ListPartitionsQuery()
    list_file_items_query = ListFileItemsQuery()

    context = ScanPartitionContext(
        emit=ScanPartitionEmitters(scanned=emit_scanned),
        query=ScanPartitionQueries(
            list_hard_drives=list_hard_drives_query.execute,
            list_partitions=list_partitions_query.execute,
            list_file_items=list_file_items_query.execute,
        )
    )

    # Define test command
    command = ScanPartition(partition_uuid="FACE862BCE85E06D")

    # Execute procedure
    procedure = ScanPartitionProcedure()

    print(f"\n{'─'*60}")
    print(f"Scanning partition: {command.partition_uuid}")
    print(f"{'─'*60}")

    procedure(context, command)
    print(f"  ✓ Scan completed")

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)
