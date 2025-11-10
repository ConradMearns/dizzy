#!/usr/bin/env python3

"""
Single-threaded DIZZY service for testing the complete command-procedure-event-policy loop.
"""

from pathlib import Path

from gen.commands import InspectStorage, AssignPartitionMount, ScanPartition
from gen.procedures import (
    InspectStorageContext, InspectStorageEmitters, InspectStorageQueries,
    AssignPartitionMountContext, AssignPartitionMountEmitters, AssignPartitionMountQueries,
    ScanPartitionContext, ScanPartitionEmitters, ScanPartitionQueries
)
from gen.policies import (
    PartitionMountAssignedPolicyContext,
    PartitionMountAssignedPolicyEmitters,
    PartitionMountAssignedPolicyQueries,
    PartitionMountAssignedPolicyMutators,
    FileItemScannedPolicyContext,
    FileItemScannedPolicyEmitters,
    FileItemScannedPolicyQueries,
    FileItemScannedPolicyMutators
)
from gen.events import HardDriveDetected, PartitionDetected, PartitionMountAssigned, FileItemScanned
from gen.mutations import EventRecordInput, EventRecord
from procedures.inspect_storage import InspectStorageProcedure
from procedures.assign_partition_mount import AssignPartitionMountProcedure
from procedures.scan_partition import ScanPartitionProcedure
from policies.partition_mount_assigned import PartitionMountAssignedPolicy
from policies.file_item_scanned import FileItemScannedPolicy
from queries.file_scanners.linux import ListHardDrivesQuery, ListPartitionsQuery, ListFileItemsQuery
from queries.cas_minio import PutContentQuery
from mutations.mount_partition import MountPartitionMutation
from mutations.append_to_manifest import AppendToManifestMutation
from gen.queries import ListPartitionsInput, ListPartitions
from gen.mutations import MountPartitionInput
from dizzy.event_store import EventRecordMutation


class Service:
    def __init__(self, data_path: Path | None = None):
        self.command_queue = []
        self.event_queue = []

        # Initialize query and mutation implementations
        list_hard_drives_query = ListHardDrivesQuery()
        list_partitions_query = ListPartitionsQuery()
        list_file_items_query = ListFileItemsQuery()
        put_content_query = PutContentQuery()
        mount_partition_mutation = MountPartitionMutation()
        append_to_manifest_mutation = AppendToManifestMutation()

        # Initialize event store mutation
        self.event_store = EventRecordMutation(base_path=data_path)

        # Event type map for deserialization (used by queries, not needed for writes)
        # When you need to query events, initialize GetAllEventsQuery or GetEventsByTypesQuery with:
        # event_type_map = {
        #     'HardDriveDetected': HardDriveDetected,
        #     'PartitionDetected': PartitionDetected,
        #     'PartitionMountAssigned': PartitionMountAssigned,
        #     'FileItemScanned': FileItemScanned,
        # }

        # Command to Procedure mapping
        self.command_map = {
            InspectStorage: [InspectStorageProcedure],
            AssignPartitionMount: [AssignPartitionMountProcedure],
            ScanPartition: [ScanPartitionProcedure],
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
            ScanPartitionProcedure: ScanPartitionContext(
                emit=ScanPartitionEmitters(
                    scanned=lambda event: self.emit_event(event),
                ),
                query=ScanPartitionQueries(
                    list_hard_drives=list_hard_drives_query.execute,
                    list_partitions=list_partitions_query.execute,
                    list_file_items=list_file_items_query.execute,
                    put_content=put_content_query.execute,
                )
            ),
        }

        # Event to Policy mapping
        self.event_map = {
            PartitionMountAssigned: [PartitionMountAssignedPolicy],
            FileItemScanned: [FileItemScannedPolicy],
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
            FileItemScannedPolicy: FileItemScannedPolicyContext(
                emit=FileItemScannedPolicyEmitters(),
                query=FileItemScannedPolicyQueries(),
                mutate=FileItemScannedPolicyMutators(
                    append_to_manifest=append_to_manifest_mutation.execute,
                )
            ),
        }

    def emit_event(self, event):
        event_input = EventRecordInput(event=event)
        event_record = self.event_store.execute(
            mutation_input=event_input,
            event_record_class=EventRecord
        )

        # Process policies for this event type (only if not a duplicate)
        if not event_record.is_duplicate and type(event) in self.event_map: 
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

                for policy_class in self.event_map[event_type]:
                    context = self.policy_map[policy_class]
                    policy = policy_class()
                    policy(context=context, event=event)


