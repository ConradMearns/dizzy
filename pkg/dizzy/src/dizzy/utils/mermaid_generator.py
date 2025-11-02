"""Mermaid diagram generator from System model."""

from pathlib import Path
from typing import Set, List, Tuple

from dizzy.utils.system_model import System


def sanitize_node_id(name: str) -> str:
    """Convert a name to a valid mermaid node ID."""
    # Replace spaces and special chars with underscores
    return name.replace(" ", "_").replace("-", "_")


def generate_mermaid_diagram(system: System) -> str:
    """
    Generate a Mermaid graph diagram from a System object.

    The diagram shows the relationships between:
    - Commands -> Procedures
    - Procedures -> Events
    - Events -> Policies
    - Policies -> Commands (cycle)
    - Procedures -> Queries
    - Policies -> Queries
    - Policies -> Mutators

    Args:
        system: System object containing all entities and relationships

    Returns:
        String containing Mermaid graph syntax
    """
    lines = ["graph TB", ""]

    # Track which nodes we've referenced to avoid duplicates
    referenced_nodes: Set[str] = set()

    # Collect all relationships
    relationships: List[Tuple[str, str, str]] = []  # (from, to, label)

    # Commands -> Procedures
    cmd_to_proc = system.get_command_to_procedure_map()
    for command_name in system.commands.keys():
        referenced_nodes.add(command_name)
        if command_name in cmd_to_proc:
            proc_name = cmd_to_proc[command_name]
            referenced_nodes.add(proc_name)
            relationships.append((command_name, proc_name, "handled by"))

    # Procedures -> Events (via emitters)
    proc_events = system.get_procedure_emitted_events()
    for proc_name, event_names in proc_events.items():
        referenced_nodes.add(proc_name)
        for event_name in event_names:
            referenced_nodes.add(event_name)
            relationships.append((proc_name, event_name, "emits"))

    # Events -> Policies
    event_to_policies = system.get_event_to_policy_map()
    for event_name, policy_names in event_to_policies.items():
        referenced_nodes.add(event_name)
        for policy_name in policy_names:
            referenced_nodes.add(policy_name)
            relationships.append((event_name, policy_name, "triggers"))

    # Policies -> Commands (via emitters)
    policy_commands = system.get_policy_emitted_commands()
    for policy_name, command_names in policy_commands.items():
        referenced_nodes.add(policy_name)
        for command_name in command_names:
            referenced_nodes.add(command_name)
            relationships.append((policy_name, command_name, "emits"))

    # Procedures -> Queries
    proc_queries = system.get_procedure_queries()
    for proc_name, query_names in proc_queries.items():
        if query_names:  # Only if there are queries
            referenced_nodes.add(proc_name)
            for query_name in query_names:
                referenced_nodes.add(query_name)
                relationships.append((proc_name, query_name, "calls"))

    # Policies -> Queries
    policy_queries = system.get_policy_queries()
    for policy_name, query_names in policy_queries.items():
        if query_names:  # Only if there are queries
            referenced_nodes.add(policy_name)
            for query_name in query_names:
                referenced_nodes.add(query_name)
                relationships.append((policy_name, query_name, "calls"))

    # Policies -> Mutators
    policy_mutators = system.get_policy_mutators()
    for policy_name, mutator_names in policy_mutators.items():
        if mutator_names:  # Only if there are mutators
            referenced_nodes.add(policy_name)
            for mutator_name in mutator_names:
                referenced_nodes.add(mutator_name)
                relationships.append((policy_name, mutator_name, "calls"))

    # Define node styles based on type
    lines.append("    %% Node definitions with styling")

    # Group nodes by type
    commands_in_diagram = [name for name in system.commands.keys() if name in referenced_nodes]
    procedures_in_diagram = [name for name in system.procedures.keys() if name in referenced_nodes]
    events_in_diagram = [name for name in system.events.keys() if name in referenced_nodes]
    policies_in_diagram = [name for name in system.policies.keys() if name in referenced_nodes]
    queries_in_diagram = [name for name in system.queries.keys() if name in referenced_nodes]
    mutators_in_diagram = [name for name in system.mutators.keys() if name in referenced_nodes]

    # Commands
    if commands_in_diagram:
        lines.append("")
        lines.append("    %% Commands")
        for cmd in commands_in_diagram:
            lines.append(f"    {sanitize_node_id(cmd)}[{cmd}]")
            lines.append(f"    style {sanitize_node_id(cmd)} fill:#e1f5ff,stroke:#01579b")

    # Procedures
    if procedures_in_diagram:
        lines.append("")
        lines.append("    %% Procedures")
        for proc in procedures_in_diagram:
            lines.append(f"    {sanitize_node_id(proc)}[{proc}]")
            lines.append(f"    style {sanitize_node_id(proc)} fill:#f3e5f5,stroke:#4a148c")

    # Events
    if events_in_diagram:
        lines.append("")
        lines.append("    %% Events")
        for event in events_in_diagram:
            lines.append(f"    {sanitize_node_id(event)}[{event}]")
            lines.append(f"    style {sanitize_node_id(event)} fill:#fff3e0,stroke:#e65100")

    # Policies
    if policies_in_diagram:
        lines.append("")
        lines.append("    %% Policies")
        for policy in policies_in_diagram:
            lines.append(f"    {sanitize_node_id(policy)}[{policy}]")
            lines.append(f"    style {sanitize_node_id(policy)} fill:#e8f5e9,stroke:#1b5e20")

    # Queries
    if queries_in_diagram:
        lines.append("")
        lines.append("    %% Queries")
        for query in queries_in_diagram:
            lines.append(f"    {sanitize_node_id(query)}[{query}]")
            lines.append(f"    style {sanitize_node_id(query)} fill:#fce4ec,stroke:#880e4f")

    # Mutators
    if mutators_in_diagram:
        lines.append("")
        lines.append("    %% Mutators")
        for mutator in mutators_in_diagram:
            lines.append(f"    {sanitize_node_id(mutator)}[{mutator}]")
            lines.append(f"    style {sanitize_node_id(mutator)} fill:#fff9c4,stroke:#f57f17")

    # Add relationships
    lines.append("")
    lines.append("    %% Relationships")
    for from_node, to_node, label in relationships:
        from_id = sanitize_node_id(from_node)
        to_id = sanitize_node_id(to_node)
        lines.append(f"    {from_id} -->|{label}| {to_id}")

    return "\n".join(lines) + "\n"


def save_mermaid_diagram(system: System, output_file: Path) -> None:
    """
    Generate and save a Mermaid diagram to a file.

    Args:
        system: System object containing all entities and relationships
        output_file: Path where the .mermaid file should be saved
    """
    diagram = generate_mermaid_diagram(system)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(diagram)
