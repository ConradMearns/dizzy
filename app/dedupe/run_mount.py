#!/usr/bin/env python3

"""
Script to run the AssignPartitionMount procedure.

This demonstrates assigning a partition to a desired mount point.
The actual mounting operation will be handled by a separate reconciliation service.
"""

from gen.commands import AssignPartitionMount, Partition
from gen.procedures import AssignPartitionMountContext, AssignPartitionMountEmitters, AssignPartitionMountQueries
from gen.events import PartitionMountAssigned
from procedures.assign_partition_mount import AssignPartitionMountProcedure


def main():
    # Event storage for investigating the event chain
    events = []

    def emit_partition_mount_assigned(event: PartitionMountAssigned) -> None:
        """Emit a PartitionMountAssigned event."""
        events.append(event)

    # Create context with emitters (no queries needed for this procedure)
    context = AssignPartitionMountContext(
        emit=AssignPartitionMountEmitters(
            partition_mount_assigned=emit_partition_mount_assigned,
        ),
        query=AssignPartitionMountQueries()
    )

    # Example: Assign the FACE862BCE85E06D partition from WP004TCG drive
    # In practice, you'd get these values from user input or previous events
    partition = Partition(
        uuid="FACE862BCE85E06D",
        drive_uuid="WP004TCG"
    )

    # Create command to assign mount point
    command = AssignPartitionMount(
        partition=partition,
        mount_point="/mnt/photos"
    )

    # Execute procedure
    procedure = AssignPartitionMountProcedure()
    procedure(context, command)

    # Display event chain summary
    print(f"\n📊 Event Chain Summary:")
    print(f"  Total events: {len(events)}")

    print(f"\n  Event details:")
    for i, event in enumerate(events, 1):
        if isinstance(event, PartitionMountAssigned):
            print(f"    {i}. PartitionMountAssigned:")
            print(f"       - Partition UUID: {event.partition.uuid}")
            print(f"       - Drive UUID: {event.partition.drive_uuid}")
            print(f"       - Mount Point: {event.mount_point}")


if __name__ == "__main__":
    main()
