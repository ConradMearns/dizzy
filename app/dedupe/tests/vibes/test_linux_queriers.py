"""
Vibe tests for Linux queriers.

These tests just ensure the code doesn't crash - we don't care about correctness.
"""

from gen.queries import ListHardDrivesInput, ListPartitionsInput
from queries.file_scanners.linux import (
    ListHardDrivesQuery,
    ListPartitionsQuery,
)


def test_list_hard_drives_doesnt_crash():
    """Just make sure ListHardDrivesQuery runs without crashing."""
    query = ListHardDrivesQuery()
    query_input = ListHardDrivesInput()
    result = query.execute(query_input)

    # Just check that we got something back
    assert result is not None
    assert hasattr(result, 'drives')
    print(f"Found {len(result.drives)} drives")


def test_list_all_partitions_doesnt_crash():
    """Just make sure ListPartitionsQuery runs without crashing (no filter)."""
    query = ListPartitionsQuery()
    query_input = ListPartitionsInput()
    result = query.execute(query_input)

    # Just check that we got something back
    assert result is not None
    assert hasattr(result, 'partitions')
    print(f"Found {len(result.partitions)} partitions")


def test_list_partitions_with_filter_doesnt_crash():
    """Just make sure ListPartitionsQuery runs without crashing (with filter)."""
    # First get a drive
    drives_query = ListHardDrivesQuery()
    drives_result = drives_query.execute(ListHardDrivesInput())

    if drives_result.drives:
        # Try filtering by the first drive
        query = ListPartitionsQuery()
        query_input = ListPartitionsInput(drive_uuid=drives_result.drives[0])
        result = query.execute(query_input)

        assert result is not None
        assert hasattr(result, 'partitions')
        print(f"Found {len(result.partitions)} partitions on drive {drives_result.drives[0]}")
