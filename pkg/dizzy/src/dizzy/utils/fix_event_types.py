"""
Fix type annotations in generated events.py.

LinkML sometimes generates incorrect types for model references.
This fixer corrects them by replacing str types with proper model types.
"""

import re
from pathlib import Path


def fix_event_types(events_file: Path, models_file: Path) -> bool:
    """
    Fix type annotations in generated events.py file.

    Args:
        events_file: Path to generated events.py
        models_file: Path to generated models.py

    Returns:
        True if fixes were applied, False otherwise
    """
    if not events_file.exists():
        return False

    content = events_file.read_text()
    original_content = content

    # Track if we made any changes
    made_changes = False

    # Fix HardDriveDetected.hard_drive: str -> HardDrive
    pattern = r'(class HardDriveDetected\([^)]+\):.*?hard_drive:\s+)str(\s+=\s+Field)'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, r'\1HardDrive\2', content, flags=re.DOTALL)
        made_changes = True

    # Fix PartitionDetected.partition: str -> Partition
    pattern = r'(class PartitionDetected\([^)]+\):.*?partition:\s+)str(\s+=\s+Field)'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, r'\1Partition\2', content, flags=re.DOTALL)
        made_changes = True

    # Write back if changes were made
    if made_changes and content != original_content:
        events_file.write_text(content)
        return True

    return False
