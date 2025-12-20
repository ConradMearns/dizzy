"""
Implementation of partition_scan procedure.

Scans partition for items, does the work of discovery. Hashes each item to ensure referential integrity.
"""

import logging
import hashlib
from pathlib import Path

from gen.procedure.py.partition_scan_context import start_scan_context
from gen.commands.pyd import start_scan

logger = logging.getLogger(__name__)


def partition_scan(context: start_scan_context, command: start_scan) -> None:
    """
    Execute the start_scan procedure.

    Scans partition for items, does the work of discovery.
    """
    scan_path = Path(command.path)

    logger.debug(f"Starting scan of path: {scan_path}")

    # Walk the directory tree
    for item_path in scan_path.rglob("*"):
        # Only process files, not directories
        if item_path.is_file():
            try:
                # Hash the file for referential integrity
                file_hash = _hash_file(item_path)

                # Log instead of emitting scan_item_found event
                logger.debug(f"Found file: {item_path} (hash: {file_hash})")

            except Exception as e:
                # Log instead of emitting scan_item_failed event
                logger.debug(f"Failed to process item: {item_path}, error: {e}")

    # Log instead of emitting scan_complete event
    logger.debug(f"Scan complete for path: {scan_path}")


def _hash_file(file_path: Path) -> str:
    """Hash a file using SHA256 for referential integrity."""
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()
