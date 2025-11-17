"""
Fix type annotations in generated code.

LinkML sometimes generates incorrect types for model references.
This fixer corrects them by replacing str types with proper model types.
"""

import re
from pathlib import Path


def fix_event_types(events_file: Path, models_file: Path = None) -> bool:
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

    # Fix PartitionMountAssigned.partition: str -> Partition
    pattern = r'(class PartitionMountAssigned\([^)]+\):.*?partition:\s+)str(\s+=\s+Field)'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, r'\1Partition\2', content, flags=re.DOTALL)
        made_changes = True

    # Write back if changes were made
    if made_changes and content != original_content:
        events_file.write_text(content)
        return True

    return False


def fix_command_types(commands_file: Path, models_file: Path = None) -> bool:
    """
    Fix type annotations in generated commands.py file.

    Args:
        commands_file: Path to generated commands.py
        models_file: Path to generated models.py (unused, for compatibility)

    Returns:
        True if fixes were applied, False otherwise
    """
    if not commands_file.exists():
        return False

    content = commands_file.read_text()
    original_content = content

    # Track if we made any changes
    made_changes = False

    # Fix AssignPartitionMount.partition: str -> Partition
    pattern = r'(class AssignPartitionMount\([^)]+\):.*?partition:\s+)str(\s+=\s+Field)'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, r'\1Partition\2', content, flags=re.DOTALL)
        made_changes = True

    # Write back if changes were made
    if made_changes and content != original_content:
        commands_file.write_text(content)
        return True

    return False


def fix_mutation_types(mutations_file: Path, models_file: Path = None) -> bool:
    """
    Fix type annotations in generated mutations.py file.

    Args:
        mutations_file: Path to generated mutations.py
        models_file: Path to generated models.py (unused, for compatibility)

    Returns:
        True if fixes were applied, False otherwise
    """
    if not mutations_file.exists():
        return False

    content = mutations_file.read_text()
    original_content = content

    # Track if we made any changes
    made_changes = False

    # Fix MountPartitionInput.partition: str -> Partition
    pattern = r'(class MountPartitionInput\([^)]+\):.*?partition:\s+)str(\s+=\s+Field)'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, r'\1Partition\2', content, flags=re.DOTALL)
        made_changes = True

    # Write back if changes were made
    if made_changes and content != original_content:
        mutations_file.write_text(content)
        return True

    return False
