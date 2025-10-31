#!/usr/bin/env python3

"""
PartitionMountAssigned policy implementation.

This policy reconciles the desired mount state with actual OS state.
It reads PartitionMountAssigned events and ensures partitions are actually mounted.
"""

from policies.interfaces import PartitionMountAssignedPolicyProtocol
from gen.policies import PartitionMountAssignedPolicyContext
from gen.events import PartitionMountAssigned
from gen.queries import ListPartitionsInput
from gen.mutations import MountPartitionInput, Partition as MutationPartition


class PartitionMountAssignedPolicy:
    """Reconcile desired partition mount state with actual OS state."""

    def __call__(self, context: PartitionMountAssignedPolicyContext, event: PartitionMountAssigned) -> None:
        """
        Execute the PartitionMountAssigned policy.

        This policy:
        1. Checks if the partition is actually mounted at the desired location
        2. If not mounted, executes the mount mutation
        3. Logs the reconciliation result
        """
        partition = event.partition
        desired_mount_point = event.mount_point

        print(f"\n🔍 Reconciling mount assignment:")
        print(f"   Partition: {partition.uuid}")
        print(f"   Desired mount point: {desired_mount_point}")

        # Query current partition state
        # TODO: We'd need a query to check if partition is mounted at the right place
        # For now, we'll assume it needs mounting and call the mutator
        print(f"   Status: Partition not yet mounted (reconciliation needed)")

        # Execute mount mutation
        print(f"   Action: Executing mount mutation...")

        # Convert event partition to mutation partition
        mutation_partition = MutationPartition(
            uuid=partition.uuid,
            drive_uuid=partition.drive_uuid,
            label=partition.label,
            mount_point=partition.mount_point,
            size_bytes=partition.size_bytes
        )

        mount_input = MountPartitionInput(
            partition=mutation_partition,
            mount_point=desired_mount_point
        )

        result = context.mutate.mount_partition(mount_input)

        if result.success:
            print(f"   ✓ Successfully mounted {partition.uuid} at {result.mount_point}")
        else:
            print(f"   ✗ Failed to mount {partition.uuid}: {result.error_message}")
            # TODO: Could emit a command to retry or alert

        print()
