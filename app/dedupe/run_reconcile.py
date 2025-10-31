#!/usr/bin/env python3

"""
Script to run the PartitionMountAssigned policy.

This demonstrates the reconciliation loop: consuming a PartitionMountAssigned event
and executing the mount mutation to align actual state with desired state.
"""

from gen.policies import (
    PartitionMountAssignedPolicyContext,
    PartitionMountAssignedPolicyEmitters,
    PartitionMountAssignedPolicyQueries,
    PartitionMountAssignedPolicyMutators
)
from gen.events import PartitionMountAssigned, Partition
from gen.commands import AssignPartitionMount
from gen.queries import ListPartitionsInput, ListPartitions
from gen.mutations import MountPartitionInput, MountPartition
from policies.partition_mount_assigned import PartitionMountAssignedPolicy
from mutations.mount_partition import MountPartitionMutation


def main():
    # Simulated event from the event stream
    # In production, this would come from reading the event store
    import os
    mount_point = os.path.expanduser("/mnt/photos")

    event = PartitionMountAssigned(
        partition=Partition(
            uuid="FACE862BCE85E06D",
            drive_uuid="WP004TCG"
        ),
        mount_point=mount_point
    )

    print("="*80)
    print("PARTITION MOUNT RECONCILIATION")
    print("="*80)
    print(f"\nReceived event: PartitionMountAssigned")
    print(f"  Partition UUID: {event.partition.uuid}")
    print(f"  Drive UUID: {event.partition.drive_uuid}")
    print(f"  Desired mount point: {event.mount_point}")

    # Track emitted commands
    emitted_commands = []

    def emit_assign_partition_mount(command: AssignPartitionMount) -> None:
        """Emit an AssignPartitionMount command (e.g., for retry)."""
        emitted_commands.append(command)
        print(f"[COMMAND EMITTED] AssignPartitionMount: {command.partition.uuid} -> {command.mount_point}")

    def list_partitions_query(input: ListPartitionsInput) -> ListPartitions:
        """Query currently mounted partitions."""
        # In production, this would query actual OS state via lsblk
        return ListPartitions(partitions=["FACE862BCE85E06D"])

    # Create real mount mutator
    mount_mutator = MountPartitionMutation()

    # Create policy context
    context = PartitionMountAssignedPolicyContext(
        emit=PartitionMountAssignedPolicyEmitters(
            assign_partition_mount=emit_assign_partition_mount
        ),
        query=PartitionMountAssignedPolicyQueries(
            list_partitions=list_partitions_query
        ),
        mutate=PartitionMountAssignedPolicyMutators(
            mount_partition=mount_mutator.execute
        )
    )

    # Execute policy
    policy = PartitionMountAssignedPolicy()
    policy(context, event)

    # Summary
    print("="*80)
    print("RECONCILIATION SUMMARY")
    print("="*80)
    print(f"Commands emitted: {len(emitted_commands)}")
    if emitted_commands:
        for cmd in emitted_commands:
            print(f"  - {cmd.__class__.__name__}")
    print()


if __name__ == "__main__":
    main()
