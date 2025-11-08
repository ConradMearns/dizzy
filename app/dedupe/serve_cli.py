#!/usr/bin/env python3

"""
CLI for running the DIZZY service with commands from JSON/JSONL files or stdin.

Usage:
    # Single command file
    python serve_cli.py commands/inspect_storage.json

    # Multiple command files (processed in order)
    python serve_cli.py commands/inspect_storage.json commands/assign_mount.json

    # From stdin (single JSON object)
    cat commands/inspect_storage.json | python serve_cli.py --stdin

    # From stdin (JSONL - multiple commands, one per line)
    cat commands/batch.jsonl | python serve_cli.py --stdin
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from gen.commands import InspectStorage, AssignPartitionMount, ScanPartition, Partition
from st_service import Service


# Command type registry - maps string types to Pydantic model classes
COMMAND_REGISTRY = {
    "InspectStorage": InspectStorage,
    "AssignPartitionMount": AssignPartitionMount,
    "ScanPartition": ScanPartition,
}


def parse_command(command_dict: Dict[str, Any]):
    """
    Parse a command dictionary into a Pydantic command object.

    Expected format:
    {
        "type": "CommandName",
        "field1": "value1",
        ...
    }
    """
    command_type = command_dict.get("type")
    if not command_type:
        raise ValueError(f"Command must have a 'type' field: {command_dict}")

    command_class = COMMAND_REGISTRY.get(command_type)
    if not command_class:
        raise ValueError(
            f"Unknown command type: {command_type}. "
            f"Available types: {list(COMMAND_REGISTRY.keys())}"
        )

    # Extract all fields except 'type'
    command_data = {k: v for k, v in command_dict.items() if k != "type"}

    # Create and validate the command using Pydantic (let it crash if invalid)
    return command_class(**command_data)


def load_commands_from_file(file_path: str) -> List:
    """
    Load commands from a JSON or JSONL file.

    - .json files: single command object
    - .jsonl files: one command per line (newline-delimited JSON)
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Command file not found: {file_path}")

    commands = []

    with open(path, 'r') as f:
        if path.suffix == ".jsonl":
            # JSONL format - one command per line
            for line in f:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                command_dict = json.loads(line)  # Let it crash with line info
                commands.append(parse_command(command_dict))
        else:
            # Regular JSON format - single command
            command_dict = json.load(f)
            commands.append(parse_command(command_dict))

    return commands


def load_commands_from_stdin() -> List:
    """
    Load commands from stdin.

    Supports both single JSON objects and JSONL (one command per line).
    Empty lines are skipped.
    """
    content = sys.stdin.read().strip()

    if not content:
        raise ValueError("No input received from stdin")

    commands = []

    # Process line by line - works for both single JSON and JSONL
    for line in content.split('\n'):
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        command_dict = json.loads(line)
        commands.append(parse_command(command_dict))

    return commands


def main():
    parser = argparse.ArgumentParser(
        description="Run DIZZY service with commands from files or stdin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Command file(s) to process (.json or .jsonl)"
    )

    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read commands from stdin instead of files"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose output (show queued commands and events)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.stdin and args.files:
        parser.error("Cannot specify both --stdin and file arguments")

    if not args.stdin and not args.files:
        parser.error("Must specify either --stdin or one or more command files")

    # Load commands
    all_commands = []

    if args.stdin:
        if args.verbose:
            print("📥 Reading commands from stdin...")
        all_commands = load_commands_from_stdin()
    else:
        for file_path in args.files:
            if args.verbose:
                print(f"📥 Loading commands from {file_path}...")
            commands = load_commands_from_file(file_path)
            all_commands.extend(commands)

    if args.verbose:
        print(f"✅ Loaded {len(all_commands)} command(s)\n")

    # Create service
    service = Service()

    # Enqueue all commands
    for i, command in enumerate(all_commands, 1):
        if args.verbose:
            print(f"📤 Enqueuing command {i}: {type(command).__name__}")
            print(f"   {command}")
        service.emit_command(command)

    if args.verbose:
        print(f"\n🚀 Running service...\n")
        print("=" * 80)

    # Run the service (processes commands and events)
    service.run()

    if args.verbose:
        print("=" * 80)
        print(f"\n✅ Service completed successfully")
        print(f"   Commands processed: {len(all_commands)}")
        print(f"   Events remaining: {len(service.event_queue)}")
        print(f"   Commands remaining: {len(service.command_queue)}")


if __name__ == "__main__":
    main()
