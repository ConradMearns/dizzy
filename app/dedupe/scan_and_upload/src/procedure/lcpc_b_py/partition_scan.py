"""
Implementation of partition_scan procedure.

Scans partition for items, does the work of discovery.
Hashes each item to ensure referential integrity.
"""

import logging
from pathlib import Path

import xxhash

from gen.commands.pyd import start_scan
from gen.procedure.py.partition_scan_context import start_scan_context


logger = logging.getLogger(__name__)


def partition_scan(context: start_scan_context, command: start_scan) -> None:
    """
    Execute the partition_scan procedure.

    Scans the filesystem path recursively, discovering files and hashing them.
    This is a first pass implementation that logs effects without emitting events.
    """
    scan_path = Path(command.path)

    logger.debug(f"Starting scan of path: {scan_path}")

    if not scan_path.exists():
        raise FileNotFoundError(f"Scan path does not exist: {scan_path}")

    if not scan_path.is_dir():
        raise NotADirectoryError(f"Scan path is not a directory: {scan_path}")

    file_count = 0

    # Recursively walk the directory tree
    for item_path in scan_path.rglob("*"):
        # Only process files, not directories
        if item_path.is_file():
            logger.debug(f"Found file: {item_path}")

            try:
                # Hash the file contents
                file_hash = _hash_file(item_path)
                logger.debug(f"Hashed file {item_path}: {file_hash}")

                file_count += 1

            except Exception as e:
                logger.debug(f"Failed to process file {item_path}: {e}")
                # Let exception propagate - runtime will handle it
                raise

    logger.debug(f"Scan complete. Processed {file_count} files from {scan_path}")


def _hash_file(file_path: Path) -> str:
    """
    Hash a file using xxHash.

    Args:
        file_path: Path to the file to hash

    Returns:
        Hexadecimal hash string
    """
    hasher = xxhash.xxh64()

    with open(file_path, "rb") as f:
        # Read in chunks to handle large files efficiently
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()
