#!/usr/bin/env python3

"""
InspectStorage procedure implementation.
"""

from procedures.interfaces import InspectStorageProcedureProtocol
from gen.procedures import InspectStorageContext
from gen.commands import InspectStorage
from gen.queries import ListHardDrivesInput, ListPartitionsInput
from gen.events import HardDriveDetected, PartitionDetected, HardDrive, Partition


class InspectStorageProcedure:
    """Inspect and display all hard drives and partitions with details."""

    def __call__(self, context: InspectStorageContext, command: InspectStorage) -> None:
        print("\n" + "="*80)
        print("STORAGE INSPECTION REPORT")
        print("="*80)

        # Get all hard drives
        print("\nQuerying hard drives...")
        hard_drives = context.query.list_hard_drives(ListHardDrivesInput())

        print(f"\nFound {len(hard_drives.drives)} hard drive(s)")
        print("\n" + "─"*80)
        print(f"{'HARD DRIVES':<80}")
        print("─"*80)

        # Emit HardDriveDetected event for each discovered drive
        for i, drive_uuid in enumerate(hard_drives.drives, 1):
            print(f"{i}. {drive_uuid}")

            # Create HardDrive model and emit event
            hard_drive = HardDrive(uuid=drive_uuid)
            context.emit.hard_drive_detected(HardDriveDetected(hard_drive=hard_drive))

        # Get all partitions
        print("\n\nQuerying partitions...")
        all_partitions = context.query.list_partitions(ListPartitionsInput())

        print(f"\nFound {len(all_partitions.partitions)} partition(s)")
        print("\n" + "─"*80)
        print(f"{'PARTITIONS':<80}")
        print("─"*80)

        for i, partition in enumerate(all_partitions.partitions, 1):
            print(f"{i}. {partition}")

        # Get partitions per drive
        print("\n\n" + "="*80)
        print("PARTITIONS BY DRIVE")
        print("="*80)

        for drive_uuid in hard_drives.drives:
            print(f"\n{drive_uuid}:")
            drive_partitions = context.query.list_partitions(
                ListPartitionsInput(drive_uuid=drive_uuid)
            )

            if drive_partitions.partitions:
                for partition_uuid in drive_partitions.partitions:
                    print(f"  └─ {partition_uuid}")

                    # Create Partition model and emit event
                    partition = Partition(uuid=partition_uuid, drive_uuid=drive_uuid)
                    context.emit.partition_detected(PartitionDetected(partition=partition))
            else:
                print("  └─ (no partitions)")

        print("\n" + "="*80)
        print("END REPORT")
        print("="*80 + "\n")


# Type check: Ensure we implement the protocol correctly
_: InspectStorageProcedureProtocol = InspectStorageProcedure()
