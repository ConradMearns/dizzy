#!/usr/bin/env python3

"""
Single-threaded DIZZY service for testing the complete command-procedure-event-policy loop.
"""

from gen.commands import InspectStorage, AssignPartitionMount
from gen.procedures import (
    InspectStorageContext, InspectStorageEmitters, InspectStorageQueries,
    AssignPartitionMountContext, AssignPartitionMountEmitters, AssignPartitionMountQueries
)
from gen.policies import (
    PartitionMountAssignedPolicyContext,
    PartitionMountAssignedPolicyEmitters,
    PartitionMountAssignedPolicyQueries,
    PartitionMountAssignedPolicyMutators
)
from gen.events import HardDriveDetected, PartitionDetected, PartitionMountAssigned
from procedures.inspect_storage import InspectStorageProcedure
from procedures.assign_partition_mount import AssignPartitionMountProcedure
from policies.partition_mount_assigned import PartitionMountAssignedPolicy
from queries.file_scanners.linux import ListHardDrivesQuery, ListPartitionsQuery
from mutations.mount_partition import MountPartitionMutation
from gen.queries import ListPartitionsInput, ListPartitions
from gen.mutations import MountPartitionInput


class Service:
    def __init__(self):
        self.command_queue = []
        self.event_queue = []

        # Initialize query and mutation implementations
        list_hard_drives_query = ListHardDrivesQuery()
        list_partitions_query = ListPartitionsQuery()
        mount_partition_mutation = MountPartitionMutation()

        # Command to Procedure mapping
        self.command_map = {
            InspectStorage: [InspectStorageProcedure],
            AssignPartitionMount: [AssignPartitionMountProcedure],
        }

        # Procedure to Context mapping
        self.procedure_map = {
            InspectStorageProcedure: InspectStorageContext(
                emit=InspectStorageEmitters(
                    hard_drive_detected=lambda event: self.emit_event(event),
                    partition_detected=lambda event: self.emit_event(event),
                ),
                query=InspectStorageQueries(
                    list_hard_drives=list_hard_drives_query.execute,
                    list_partitions=list_partitions_query.execute,
                )
            ),
            AssignPartitionMountProcedure: AssignPartitionMountContext(
                emit=AssignPartitionMountEmitters(
                    partition_mount_assigned=lambda event: self.emit_event(event),
                ),
                query=AssignPartitionMountQueries()
            ),
        }

        # Event to Policy mapping
        self.event_map = {
            PartitionMountAssigned: [PartitionMountAssignedPolicy],
            # HardDriveDetected and PartitionDetected don't have policies yet
        }

        # Policy to Context mapping
        self.policy_map = {
            PartitionMountAssignedPolicy: PartitionMountAssignedPolicyContext(
                emit=PartitionMountAssignedPolicyEmitters(
                    assign_partition_mount=lambda command: self.emit_command(command),
                ),
                query=PartitionMountAssignedPolicyQueries(
                    list_partitions=list_partitions_query.execute,
                ),
                mutate=PartitionMountAssignedPolicyMutators(
                    mount_partition=mount_partition_mutation.execute,
                )
            ),
        }

    def emit_event(self, event):
        self.event_queue.append(event)

    def emit_command(self, command):
        self.command_queue.append(command)

    def run(self):
        while self.command_queue or self.event_queue:
            while self.command_queue:
                command = self.command_queue.pop(0)  # FIFO
                for procedure_class in self.command_map[type(command)]:
                    context = self.procedure_map[procedure_class]
                    procedure = procedure_class()
                    procedure(context=context, command=command)

            while self.event_queue:
                event = self.event_queue.pop(0)  # FIFO
                event_type = type(event)
                if event_type in self.event_map:
                    for policy_class in self.event_map[event_type]:
                        context = self.policy_map[policy_class]
                        policy = policy_class()
                        policy(context=context, event=event)


