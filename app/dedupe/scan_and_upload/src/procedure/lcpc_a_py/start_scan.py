"""
Implementation of start_scan procedure (partition_scan).

Scans a filesystem path to discover files (not folders).
"""

import logging
from pathlib import Path

from gen.procedure.py.partition_scan_context import start_scan_context
from gen.commands.pyd import start_scan

logger = logging.getLogger(__name__)


def start_scan_procedure(context: start_scan_context, command: start_scan) -> None:
    """
    Execute the start_scan procedure.

    Scans partition for items, does the work of discovery.
    Walks the filesystem at the given path and discovers all files.
    """
    scan_path = Path(command.path)

    logger.debug(f"Starting scan of path: {scan_path}")

    # Validate path exists
    if not scan_path.exists():
        logger.error(f"Scan path does not exist: {scan_path}")
        raise FileNotFoundError(f"Path does not exist: {scan_path}")

    if not scan_path.is_dir():
        logger.error(f"Scan path is not a directory: {scan_path}")
        raise NotADirectoryError(f"Path is not a directory: {scan_path}")

    # Walk the directory tree and discover files
    file_count = 0
    for item_path in scan_path.rglob("*"):
        if item_path.is_file():
            logger.debug(f"Found file: {item_path}")
            # Future: emit scan_item_found event here
            file_count += 1

    logger.debug(f"Scan complete. Found {file_count} files in {scan_path}")
    # Future: emit scan_complete event here
