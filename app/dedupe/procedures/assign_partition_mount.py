#!/usr/bin/env python3

"""
AssignPartitionMount procedure implementation.
"""

from procedures.interfaces import AssignPartitionMountProcedureProtocol
from gen.procedures import AssignPartitionMountContext
from gen.commands import AssignPartitionMount
from gen.events import PartitionMountAssigned


class AssignPartitionMountProcedure:
    """Assign a partition to a mount point, recording the desired state."""

    def __call__(self, context: AssignPartitionMountContext, command: AssignPartitionMount) -> None:
        """
        Execute the AssignPartitionMount procedure.

        This is a lightweight procedure that simply validates the command
        and emits the PartitionMountAssigned event to record the desired state.
        Actual mounting will be handled by a separate reconciliation service.
        """
        # Validate that mount_point is an absolute path
        if not command.mount_point.startswith('/'):
            raise ValueError(f"Mount point must be an absolute path, got: {command.mount_point}")

        # Emit the desired state event (partition is a UUID string)
        context.emit.partition_mount_assigned(
            PartitionMountAssigned(
                partition=command.partition,
                mount_point=command.mount_point
            )
        )

        print(f"✓ Assigned partition {command.partition} to mount point {command.mount_point}")
