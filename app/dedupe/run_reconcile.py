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
    # Simulated events from the event stream
    # In production, this would come from reading the event store
    import os

    # Define partitions to mount (from manifesting.md)
    partitions_to_mount = [
        {"uuid": "B0E2ACBDE2AC8964", "device": "/dev/sda3", "mount_point": "/mnt/dedupe_a"},
        {"uuid": "FACE862BCE85E06D", "device": "/dev/sdd2", "mount_point": "/mnt/dedupe_b"},
        {"uuid": "94BA918FBA916F0C", "device": "/dev/sde2", "mount_point": "/mnt/dedupe_c"},
        {"uuid": "784A20BF4A207C4E", "device": "/dev/sdf1", "mount_point": "/mnt/dedupe_d"},
    ]

    print("="*80)
    print("PARTITION MOUNT RECONCILIATION")
    print("="*80)
    print(f"\nProcessing {len(partitions_to_mount)} partitions...")
    print("\nNote: /dev/sdb1 skipped (no UUID, only PARTUUID)")
    print()

    events = []
    for p in partitions_to_mount:
        event = PartitionMountAssigned(
            partition=Partition(
                uuid=p["uuid"],
                drive_uuid="UNKNOWN"  # We don't have drive UUIDs yet
            ),
            mount_point=p["mount_point"]
        )
        events.append((p, event))

    for p, event in events:
        print(f"\n{'='*80}")
        print(f"Processing: {p['device']} (UUID: {p['uuid'][:16]}...)")
        print(f"  Desired mount point: {event.mount_point}")
        print(f"{'='*80}")

    # Track emitted commands
    emitted_commands = []

    def emit_assign_partition_mount(command: AssignPartitionMount) -> None:
        """Emit an AssignPartitionMount command (e.g., for retry)."""
        emitted_commands.append(command)
        print(f"[COMMAND EMITTED] AssignPartitionMount: {command.partition.uuid} -> {command.mount_point}")

    def list_partitions_query(input: ListPartitionsInput) -> ListPartitions:
        """Query currently mounted partitions."""
        # In production, this would query actual OS state via lsblk
        return ListPartitions(partitions=[p["uuid"] for p in partitions_to_mount])

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

    # Execute policy for each event
    policy = PartitionMountAssignedPolicy()
    for p, event in events:
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
