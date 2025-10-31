"""
MountPartition mutation implementation.

This mutation performs the actual OS-level mount operation.
"""

import subprocess
from pathlib import Path
from gen.mutations import MountPartitionInput, MountPartition


class MountPartitionMutation:
    """Execute the actual partition mount operation."""

    def execute(self, input: MountPartitionInput) -> MountPartition:
        """
        Mount a partition at the specified mount point.

        Args:
            input: MountPartitionInput with partition and mount_point

        Returns:
            MountPartition with success status and optional error message
        """
        partition_uuid = input.partition.uuid
        mount_point = input.mount_point

        print(f"[MUTATOR] Mounting partition {partition_uuid} at {mount_point}")

        # Ensure mount point directory exists using sudo
        mount_path = Path(mount_point)
        if not mount_path.exists():
            mkdir_cmd = ["sudo", "mkdir", "-p", mount_point]
            print(f"[MUTATOR] $ {' '.join(mkdir_cmd)}")
            try:
                subprocess.run(
                    mkdir_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"[MUTATOR] ✓ Mount point directory created: {mount_point}")
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else str(e)
                return MountPartition(
                    success=False,
                    partition_uuid=partition_uuid,
                    mount_point=mount_point,
                    error_message=f"Failed to create mount point directory: {error_msg}"
                )
        else:
            print(f"[MUTATOR] ✓ Mount point directory exists: {mount_point}")

        # Execute mount command
        device_path = f"/dev/disk/by-uuid/{partition_uuid}"
        mount_cmd = ["sudo", "mount", device_path, mount_point]

        print(f"[MUTATOR] $ {' '.join(mount_cmd)}")

        try:
            result = subprocess.run(
                mount_cmd,
                capture_output=True,
                text=True,
                check=True
            )

            print(f"[MUTATOR] ✓ Mount operation completed successfully")

            return MountPartition(
                success=True,
                partition_uuid=partition_uuid,
                mount_point=mount_point
            )

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            print(f"[MUTATOR] ✗ Mount failed: {error_msg}")

            return MountPartition(
                success=False,
                partition_uuid=partition_uuid,
                mount_point=mount_point,
                error_message=error_msg
            )

        except FileNotFoundError:
            error_msg = "mount command not found - is util-linux installed?"
            print(f"[MUTATOR] ✗ {error_msg}")

            return MountPartition(
                success=False,
                partition_uuid=partition_uuid,
                mount_point=mount_point,
                error_message=error_msg
            )
