"""
AppendToManifest mutation implementation.

This mutation appends file metadata to partition-specific manifest CSV files.
"""

import csv
from pathlib import Path
from gen.mutations import AppendToManifestInput, AppendToManifest


class AppendToManifestMutation:
    """Append file entry to a partition manifest CSV."""

    def __init__(self, manifest_base_dir: str = "manifests"):
        """
        Initialize the mutation with a base directory for manifests.

        Args:
            manifest_base_dir: Base directory where manifest CSVs are stored
        """
        self.manifest_base_dir = Path(manifest_base_dir)

    def execute(self, input: AppendToManifestInput) -> AppendToManifest:
        """
        Append a file entry to the partition's manifest CSV.

        The CSV format is:
        partition_uuid,path,cas_id,content_hash,size

        Args:
            input: AppendToManifestInput with file metadata

        Returns:
            AppendToManifest with success status and manifest path
        """
        # Ensure manifest directory exists
        self.manifest_base_dir.mkdir(parents=True, exist_ok=True)

        # Construct manifest file path
        manifest_file = self.manifest_base_dir / f"{input.partition_uuid}.csv"

        print(f"[MUTATOR] Appending to manifest: {manifest_file}")

        try:
            # Check if file exists to determine if we need to write header
            file_exists = manifest_file.exists()

            # Open file in append mode
            with manifest_file.open('a', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write header if this is a new file
                if not file_exists:
                    writer.writerow([
                        'partition_uuid',
                        'path',
                        'cas_id',
                        'content_hash',
                        'size'
                    ])
                    print(f"[MUTATOR] ✓ Created new manifest with header")

                # Write the file entry
                writer.writerow([
                    input.partition_uuid,
                    input.path,
                    input.cas_id,
                    input.content_hash,
                    input.size
                ])

            print(f"[MUTATOR] ✓ Successfully appended entry to manifest")

            return AppendToManifest(
                success=True,
                manifest_path=str(manifest_file)
            )

        except Exception as e:
            error_msg = str(e)
            print(f"[MUTATOR] ✗ Failed to append to manifest: {error_msg}")

            return AppendToManifest(
                success=False,
                manifest_path=str(manifest_file),
                error_message=error_msg
            )
