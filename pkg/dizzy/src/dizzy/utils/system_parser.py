"""Parser for loading LinkML schemas into a System model."""

import yaml
from pathlib import Path
from typing import Optional

from dizzy.utils.system_model import System, Command, Event, Query, Mutator, Procedure, Policy


def parse_yaml_file(file_path: Path) -> dict:
    """Parse a YAML file and return the contents."""
    if not file_path.exists():
        return {}

    with open(file_path, 'r') as f:
        return yaml.safe_load(f) or {}


def parse_commands(def_dir: Path, system: System) -> None:
    """Parse commands.yaml and populate the system."""
    commands_yaml = parse_yaml_file(def_dir / "commands.yaml")

    classes = commands_yaml.get("classes", {})
    for class_name, class_def in classes.items():
        # Skip if this is the base Command class or other base classes
        if class_name == "Command" or not isinstance(class_def, dict):
            continue

        # Check if this class inherits from Command
        is_a = class_def.get("is_a")
        if is_a == "Command":
            system.commands[class_name] = Command(
                name=class_name,
                description=class_def.get("description", "").strip()
            )


def parse_events(def_dir: Path, system: System) -> None:
    """Parse events.yaml and populate the system."""
    events_yaml = parse_yaml_file(def_dir / "events.yaml")

    classes = events_yaml.get("classes", {})
    for class_name, class_def in classes.items():
        # Skip if this is the base DomainEvent class
        if class_name == "DomainEvent" or not isinstance(class_def, dict):
            continue

        # Check if this class inherits from DomainEvent
        is_a = class_def.get("is_a")
        if is_a == "DomainEvent":
            system.events[class_name] = Event(
                name=class_name,
                description=class_def.get("description", "").strip()
            )


def parse_queries(def_dir: Path, system: System) -> None:
    """Parse queries.yaml and populate the system."""
    queries_yaml = parse_yaml_file(def_dir / "queries.yaml")

    classes = queries_yaml.get("classes", {})
    for class_name, class_def in classes.items():
        # Skip if this is the base Query class or QueryInput
        if class_name in ("Query", "QueryInput") or not isinstance(class_def, dict):
            continue

        # Check if this class inherits from Query (not QueryInput)
        is_a = class_def.get("is_a")
        if is_a == "Query":
            system.queries[class_name] = Query(
                name=class_name,
                description=class_def.get("description", "").strip()
            )


def parse_mutations(def_dir: Path, system: System) -> None:
    """Parse mutations.yaml and populate the system."""
    mutations_yaml = parse_yaml_file(def_dir / "mutations.yaml")

    classes = mutations_yaml.get("classes", {})
    for class_name, class_def in classes.items():
        # Skip if this is the base Mutation class or MutationInput
        if class_name in ("Mutation", "MutationInput") or not isinstance(class_def, dict):
            continue

        # Check if this class inherits from Mutation (not MutationInput)
        is_a = class_def.get("is_a")
        if is_a == "Mutation":
            system.mutators[class_name] = Mutator(
                name=class_name,
                description=class_def.get("description", "").strip()
            )


def parse_procedures(def_dir: Path, system: System) -> None:
    """Parse procedures.d.yaml and populate the system."""
    procedures_yaml = parse_yaml_file(def_dir / "procedures.d.yaml")

    procedures = procedures_yaml.get("procedures", {})
    for proc_name, proc_def in procedures.items():
        emitters = proc_def.get("emitters", {})
        queries = proc_def.get("queries", {})

        system.procedures[proc_name] = Procedure(
            name=proc_name,
            command=proc_def.get("command", ""),
            emitters=emitters if emitters else {},
            queries=queries if queries else {}
        )


def parse_policies(def_dir: Path, system: System) -> None:
    """Parse policies.d.yaml and populate the system."""
    policies_yaml = parse_yaml_file(def_dir / "policies.d.yaml")

    policies = policies_yaml.get("policies", {})
    for policy_name, policy_def in policies.items():
        emitters = policy_def.get("emitters", {})
        queries = policy_def.get("queries", {})
        mutators = policy_def.get("mutators", {})

        system.policies[policy_name] = Policy(
            name=policy_name,
            event=policy_def.get("event", ""),
            emitters=emitters if emitters else {},
            queries=queries if queries else {},
            mutators=mutators if mutators else {}
        )


def load_system(def_dir: Path) -> System:
    """
    Load all LinkML schemas from a def directory and return a System object.

    Args:
        def_dir: Path to the directory containing LinkML YAML files

    Returns:
        System object containing all parsed entities and relationships
    """
    system = System()

    # Parse all the YAML files
    parse_commands(def_dir, system)
    parse_events(def_dir, system)
    parse_queries(def_dir, system)
    parse_mutations(def_dir, system)
    parse_procedures(def_dir, system)
    parse_policies(def_dir, system)

    return system
