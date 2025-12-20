#!/usr/bin/env python3
"""
Experimental script to generate LinkML schema files from a Dizzy feature definition.
Creates individual files for each command and event.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict

import yaml


def calculate_relative_path(from_dir: Path, to_file: Path) -> str:
    """Calculate relative path from one directory to a file."""
    try:
        rel_path = os.path.relpath(to_file, from_dir)
        # Remove the .yaml extension for LinkML imports
        if rel_path.endswith('.yaml'):
            rel_path = rel_path[:-5]
        return rel_path
    except ValueError:
        # On Windows, if paths are on different drives, use absolute path
        return str(to_file)


def generate_event_schema(event_name: str, event_description: str, domain_name: str, base_event_path: str) -> Dict:
    """Generate LinkML schema for a single domain event."""
    class_name = event_name

    schema = {
        "id": f"https://example.org/{domain_name}/events/{event_name}",
        "name": f"{domain_name}-{event_name}-event",
        "title": f"{class_name} Event",
        "description": event_description or f"Event: {event_name}",
        "prefixes": {
            "linkml": "https://w3id.org/linkml/",
            domain_name: f"https://example.org/{domain_name}/",
        },
        "default_prefix": domain_name,
        "default_range": "string",
        "imports": [
            "linkml:types",
            base_event_path,
        ],
        "classes": {
            class_name: {
                "description": event_description or f"Event: {event_name}",
                "is_a": "Event",
                "attributes": {
                    "event_id": {
                        "description": f"Unique identifier for this {event_name} event",
                        "required": True,
                        "range": "string",
                    },
                },
            }
        },
    }

    return schema


def generate_command_schema(command_name: str, command_description: str, domain_name: str, base_command_path: str) -> Dict:
    """Generate LinkML schema for a single command."""
    class_name = command_name

    schema = {
        "id": f"https://example.org/{domain_name}/commands/{command_name}",
        "name": f"{domain_name}-{command_name}-command",
        "title": f"{class_name} Command",
        "description": command_description or f"Command: {command_name}",
        "prefixes": {
            "linkml": "https://w3id.org/linkml/",
            domain_name: f"https://example.org/{domain_name}/",
        },
        "default_prefix": domain_name,
        "default_range": "string",
        "imports": [
            "linkml:types",
            base_command_path,
        ],
        "classes": {
            class_name: {
                "description": command_description or f"Command: {command_name}",
                "is_a": "Command",
                "attributes": {
                    "command_id": {
                        "description": f"Unique identifier for this {command_name} command",
                        "required": True,
                        "range": "string",
                    },
                },
            }
        },
    }

    return schema


def write_schema_file(output_path: Path, schema: Dict, fresh: bool):
    """Write schema to file, preserving existing content unless fresh=True."""
    if output_path.exists() and not fresh:
        print(f"  Skipping {output_path} (already exists, use --fresh to overwrite)")
        return

    with open(output_path, "w") as f:
        yaml.dump(schema, f, default_flow_style=False, sort_keys=False)

    status = "Overwritten" if output_path.exists() and fresh else "Created"
    print(f"  {status}: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate LinkML schema files from a Dizzy feature definition"
    )
    parser.add_argument("feature_file", help="Path to the feature YAML file")
    parser.add_argument("output_dir", help="Directory to write LinkML schema files")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Overwrite existing files (otherwise preserves them)",
    )

    args = parser.parse_args()

    feature_path = Path(args.feature_file)
    output_dir = Path(args.output_dir)

    if not feature_path.exists():
        print(f"Error: Feature file {feature_path} does not exist")
        sys.exit(1)

    # Load the feature YAML using safe_load (plain Python dicts/strings)
    print(f"Loading feature from {feature_path}...")
    with open(feature_path) as f:
        feature_data = yaml.safe_load(f)

    # Determine domain name from path (e.g., app/dedupe/... -> dedupe)
    domain_name = feature_path.parent.name

    # Create output directories
    events_dir = output_dir / "events"
    commands_dir = output_dir / "commands"
    events_dir.mkdir(parents=True, exist_ok=True)
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Find the base Dizzy schema files
    dizzy_base_dir = Path(__file__).parent / "dizzy" / "src" / "dizzy" / "def"
    base_events_file = dizzy_base_dir / "events.yaml"
    base_commands_file = dizzy_base_dir / "commands.yaml"

    # Calculate relative paths from output directories to base schemas
    base_event_path = calculate_relative_path(events_dir.absolute(), base_events_file.absolute())
    base_command_path = calculate_relative_path(commands_dir.absolute(), base_commands_file.absolute())

    print(f"Base event schema path: {base_event_path}")
    print(f"Base command schema path: {base_command_path}")

    # Generate event schemas
    print(f"\nGenerating event schemas for domain '{domain_name}'...")
    events = feature_data.get("events", {})
    if events:
        for event_name, event_description in events.items():
            event_schema = generate_event_schema(
                event_name, event_description, domain_name, base_event_path
            )
            output_path = events_dir / f"{event_name}.yaml"
            write_schema_file(output_path, event_schema, args.fresh)
    else:
        print("  No events found in feature")

    # Generate command schemas
    print(f"\nGenerating command schemas for domain '{domain_name}'...")
    commands = feature_data.get("commands", {})
    if commands:
        for command_name, command_description in commands.items():
            command_schema = generate_command_schema(
                command_name, command_description, domain_name, base_command_path
            )
            output_path = commands_dir / f"{command_name}.yaml"
            write_schema_file(output_path, command_schema, args.fresh)
    else:
        print("  No commands found in feature")

    print("\nDone!")
    print("\nNote: Generated schemas have minimal placeholder attributes.")
    print("Edit each file to add domain-specific attributes as needed.")


if __name__ == "__main__":
    main()
