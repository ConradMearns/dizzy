"""
Linux-specific implementations for file scanning queries.

HIDDEN DEPENDENCIES:
- Platform: Linux only (uses lsblk)
- Command: lsblk must be installed and available in PATH
"""

import json
import subprocess
from gen.queries import (
    ListHardDrivesInput,
    ListHardDrives,
    ListPartitionsInput,
    ListPartitions,
    ListFileItemsInput,
    ListFileItems,
)


class ListHardDrivesQuery:
    """Linux implementation for listing hard drives using lsblk."""

    def execute(self, query_input: ListHardDrivesInput) -> ListHardDrives:
        result = subprocess.run(
            ['lsblk', '-J', '-b', '-o', 'NAME,SERIAL,TYPE'],
            capture_output=True,
            text=True
        )

        data = json.loads(result.stdout)
        drive_serials = []

        for device in data['blockdevices']:
            if device['type'] == 'disk' and device.get('serial'):
                drive_serials.append(device['serial'])

        return ListHardDrives(drives=drive_serials)


class ListPartitionsQuery:
    """Linux implementation for listing partitions using lsblk."""

    def execute(self, query_input: ListPartitionsInput) -> ListPartitions:
        result = subprocess.run(
            ['lsblk', '-J', '-b', '-o', 'NAME,UUID,SERIAL,TYPE,PKNAME'],
            capture_output=True,
            text=True
        )

        data = json.loads(result.stdout)
        partition_uuids = []

        for device in data['blockdevices']:
            if device['type'] == 'disk' and device.get('serial'):
                drive_serial = device['serial']

                # If filtering by drive_uuid, check if this is the right drive
                if query_input.drive_uuid and drive_serial != query_input.drive_uuid:
                    continue

                # Collect partitions from this drive
                if 'children' in device:
                    for child in device['children']:
                        if child['type'] == 'part' and child.get('uuid'):
                            partition_uuids.append(child['uuid'])

        return ListPartitions(partitions=partition_uuids)


class ListFileItemsQuery:
    """Linux implementation for listing file items using find."""

    def execute(self, query_input: ListFileItemsInput) -> ListFileItems:
        # First, find the mount point for this partition UUID
        result = subprocess.run(
            ['lsblk', '-J', '-o', 'UUID,MOUNTPOINT'],
            capture_output=True,
            text=True
        )

        data = json.loads(result.stdout)
        mount_point = None

        for device in data['blockdevices']:
            if device.get('uuid') == query_input.partition_uuid:
                mount_point = device.get('mountpoint')
                break
            if 'children' in device:
                for child in device['children']:
                    if child.get('uuid') == query_input.partition_uuid:
                        mount_point = child.get('mountpoint')
                        break

        if not mount_point:
            return ListFileItems(file_items=[])

        # Use find to list all files (returns paths as strings for now)
        result = subprocess.run(
            ['find', mount_point, '-type', 'f'],
            capture_output=True,
            text=True
        )

        file_paths = [line for line in result.stdout.strip().split('\n') if line]

        return ListFileItems(file_items=file_paths)
