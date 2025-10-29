#!/usr/bin/env python3

"""
Script to run the InspectStorage procedure.
"""

from gen.commands import InspectStorage
from gen.procedures import InspectStorageContext, InspectStorageQueries, InspectStorageEmitters
from gen.events import HardDriveDetected, PartitionDetected
from queries.file_scanners.linux import ListHardDrivesQuery, ListPartitionsQuery
from procedures.inspect_storage import InspectStorageProcedure


def main():
    # Event storage for investigating the event chain
    events = []

    def emit_hard_drive_detected(event: HardDriveDetected) -> None:
        """Emit a HardDriveDetected event."""
        events.append(event)

    def emit_partition_detected(event: PartitionDetected) -> None:
        """Emit a PartitionDetected event."""
        events.append(event)

    # Create context with real Linux query implementations and emitters
    context = InspectStorageContext(
        emit=InspectStorageEmitters(
            hard_drive_detected=emit_hard_drive_detected,
            partition_detected=emit_partition_detected,
        ),
        query=InspectStorageQueries(
            list_hard_drives=ListHardDrivesQuery().execute,
            list_partitions=ListPartitionsQuery().execute,
        )
    )

    # Create command
    command = InspectStorage()

    # Execute procedure
    procedure = InspectStorageProcedure()
    procedure(context, command)

    # Display event chain summary
    print(f"\n📊 Event Chain Summary:")
    print(f"  Total events: {len(events)}")
    print(f"\n  Events by type:")
    hard_drive_events = [e for e in events if isinstance(e, HardDriveDetected)]
    partition_events = [e for e in events if isinstance(e, PartitionDetected)]
    print(f"    - HardDriveDetected: {len(hard_drive_events)}")
    print(f"    - PartitionDetected: {len(partition_events)}")

    print(f"\n  Event details:")
    for i, event in enumerate(events, 1):
        if isinstance(event, HardDriveDetected):
            print(f"    {i}. HardDriveDetected(uuid={event.hard_drive.uuid})")
        elif isinstance(event, PartitionDetected):
            print(f"    {i}. PartitionDetected(uuid={event.partition.uuid}, drive_uuid={event.partition.drive_uuid})")


if __name__ == "__main__":
    main()
