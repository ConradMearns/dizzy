#!/usr/bin/env python3

import json
import subprocess
from gen.models import HardDrive, Partition

# Get all block devices with partitions using lsblk
result = subprocess.run(
    ['lsblk', '-J', '-o', 'NAME,UUID,LABEL,MOUNTPOINT,TYPE,PKNAME,SERIAL'],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)

drives = {}
partitions = []
name_to_serial = {}

# First pass: collect all drives
for device in data['blockdevices']:
    if device['type'] == 'disk' and device.get('serial'):
        serial = device['serial']
        name_to_serial[device['name']] = serial
        drives[device['name']] = HardDrive(
            uuid=serial,
            label=device.get('label')
        )

        # Check for partitions on this drive
        if 'children' in device:
            for child in device['children']:
                if child['type'] == 'part' and child.get('uuid'):
                    partition = Partition(
                        uuid=child['uuid'],
                        drive_uuid=serial,
                        label=child.get('label'),
                        mount_point=child.get('mountpoint')
                    )
                    partitions.append(partition)

# Print all drives
print("=== HARD DRIVES ===")
for name, drive in drives.items():
    print(f"Drive: {name}")
    print(f"  Serial: {drive.uuid}")
    print(f"  Label: {drive.label}")
    print()

# Print all partitions
print("=== PARTITIONS ===")
for partition in partitions:
    print(f"Partition UUID: {partition.uuid}")
    print(f"  Drive Serial: {partition.drive_uuid}")
    print(f"  Label: {partition.label}")
    print(f"  Mount Point: {partition.mount_point}")
    print()

print(f"Total drives found: {len(drives)}")
print(f"Total partitions found: {len(partitions)}")
