"""CLI for dizzy code generation."""

import typer
from pathlib import Path
from typing import Optional
import subprocess
from enum import Enum

from dizzy.utils.generate_query_interfaces import generate_query_interfaces
from dizzy.utils.generate_mutation_interfaces import generate_mutation_interfaces
from dizzy.utils.generate_procedure_contexts import generate_procedure_contexts
from dizzy.utils.generate_policy_contexts import generate_policy_contexts
from dizzy.utils.fix_event_types import fix_event_types, fix_command_types, fix_mutation_types
from dizzy.utils.system_parser import load_system
from dizzy.utils.mermaid_generator import save_mermaid_diagram

app = typer.Typer()


class EntityType(str, Enum):
    """Types of entities that can be listed."""
    commands = "commands"
    events = "events"
    queries = "queries"
    mutators = "mutators"
    procedures = "procedures"
    policies = "policies"


def run_gen_pydantic(schema_file: Path, output_file: Path) -> bool:
    """Run gen-pydantic to generate Pydantic models from LinkML schema."""
    try:
        result = subprocess.run(
            ["gen-pydantic", str(schema_file)],
            capture_output=True,
            text=True,
            check=True
        )
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result.stdout)
        
        print(f"✓ {output_file.name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ {output_file.name}: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ gen-pydantic not found. Install linkml: uv add linkml")
        return False


@app.command()
def gen(
    def_dir: Path = typer.Option(
        "def",
        "--def-dir",
        help="Directory containing LinkML schema files"
    ),
    gen_dir: Path = typer.Option(
        "gen",
        "--gen-dir",
        help="Output directory for all generated code"
    ),
):
    """Generate code from LinkML schemas."""
    def_dir = def_dir.resolve()
    gen_dir = gen_dir.resolve()

    # Calculate base directory from def_dir parent
    base_dir = def_dir.parent
    queries_dir = base_dir / "queries"
    mutations_dir = base_dir / "mutations"
    procedures_dir = base_dir / "procedures"
    policies_dir = base_dir / "policies"

    if not def_dir.exists():
        print(f"✗ def/ directory not found at {def_dir}")
        raise typer.Exit(1)

    print(f"Generating from {def_dir}/ to {gen_dir}/\n")
    
    success = True
    
    # Generate Pydantic models
    print("Pydantic models:")
    schemas = [
        ("models.yaml", "models.py"),
        ("commands.yaml", "commands.py"),
        ("queries.yaml", "queries.py"),
        ("events.yaml", "events.py"),
        ("mutations.yaml", "mutations.py"),
    ]
    
    for schema_name, output_name in schemas:
        schema_file = def_dir / schema_name
        output_file = gen_dir / output_name

        if schema_file.exists():
            if not run_gen_pydantic(schema_file, output_file):
                success = False

    # Apply custom fixes
    print("\nCustom fixes:")
    events_file = gen_dir / "events.py"
    commands_file = gen_dir / "commands.py"
    mutations_file = gen_dir / "mutations.py"
    models_file = gen_dir / "models.py"

    fixes_applied = False
    if events_file.exists() and fix_event_types(events_file, models_file):
        print("✓ Fixed event type annotations")
        fixes_applied = True

    if commands_file.exists() and fix_command_types(commands_file, models_file):
        print("✓ Fixed command type annotations")
        fixes_applied = True

    if mutations_file.exists() and fix_mutation_types(mutations_file, models_file):
        print("✓ Fixed mutation type annotations")
        fixes_applied = True

    if not fixes_applied:
        print("  No fixes needed")

    # Query interfaces
    print("\nQuery interfaces:")
    queries_yaml = def_dir / "queries.yaml"
    if queries_yaml.exists():
        try:
            generate_query_interfaces(
                queries_yaml,
                queries_dir / "interfaces.py",
                gen_import_path="gen.queries"
            )
        except Exception as e:
            print(f"✗ queries/interfaces.py: {e}")
            success = False
    
    # Mutation interfaces
    print("\nMutation interfaces:")
    mutations_yaml = def_dir / "mutations.yaml"
    if mutations_yaml.exists():
        try:
            generate_mutation_interfaces(
                mutations_yaml,
                mutations_dir / "interfaces.py",
                gen_import_path="gen.mutations"
            )
        except Exception as e:
            print(f"✗ mutations/interfaces.py: {e}")
            success = False
    
    # Procedure contexts
    print("\nProcedure contexts:")
    procedures_yaml = def_dir / "procedures.d.yaml"
    if procedures_yaml.exists():
        try:
            generate_procedure_contexts(
                procedures_yaml,
                gen_dir / "procedures.py",
                procedures_dir / "interfaces.py",
            )
        except Exception as e:
            print(f"✗ procedures: {e}")
            success = False

    # Policy contexts
    print("\nPolicy contexts:")
    policies_yaml = def_dir / "policies.d.yaml"
    if policies_yaml.exists():
        try:
            generate_policy_contexts(
                policies_yaml,
                gen_dir / "policies.py",
                policies_dir / "interfaces.py",
            )
        except Exception as e:
            print(f"✗ policies: {e}")
            success = False

    print()
    if success:
        print("✨ Done")
        raise typer.Exit(0)
    else:
        print("⚠️  Completed with errors")
        raise typer.Exit(1)


@app.command()
def list(
    entity_type: EntityType = typer.Argument(
        ...,
        help="Type of entity to list"
    ),
    def_dir: Path = typer.Argument(
        "def",
        help="Directory containing LinkML schema files"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show descriptions for each entity"
    ),
):
    """List entities of a specific type from LinkML schemas."""
    def_dir = def_dir.resolve()

    if not def_dir.exists():
        print(f"✗ def/ directory not found at {def_dir}")
        raise typer.Exit(1)

    try:
        # Load the system from YAML files
        system = load_system(def_dir)

        # Get the appropriate dictionary based on entity type
        entities_map = {
            EntityType.commands: system.commands,
            EntityType.events: system.events,
            EntityType.queries: system.queries,
            EntityType.mutators: system.mutators,
            EntityType.procedures: system.procedures,
            EntityType.policies: system.policies,
        }

        entities = entities_map[entity_type]

        if not entities:
            print(f"No {entity_type.value} found in {def_dir}")
            return

        print(f"\n{entity_type.value.capitalize()} ({len(entities)}):")
        print()

        for name, entity in sorted(entities.items()):
            if verbose and hasattr(entity, 'description') and entity.description:
                # Clean up description for display
                desc = entity.description.replace('\n', ' ').strip()
                # Truncate if too long
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                print(f"  • {name}")
                print(f"    {desc}")
            else:
                print(f"  • {name}")

        print()

    except Exception as e:
        print(f"✗ Error listing {entity_type.value}: {e}")
        raise typer.Exit(1)


@app.command()
def diagram(
    def_dir: Path = typer.Option(
        "def",
        "--def-dir",
        help="Directory containing LinkML schema files"
    ),
    output: Path = typer.Option(
        "architecture.mermaid",
        "--output",
        "-o",
        help="Output file path for the Mermaid diagram"
    ),
):
    """Generate a Mermaid diagram from LinkML schemas."""
    def_dir = def_dir.resolve()
    output = output.resolve()

    if not def_dir.exists():
        print(f"✗ def/ directory not found at {def_dir}")
        raise typer.Exit(1)

    print(f"Loading system from {def_dir}/")

    try:
        # Load the system from YAML files
        system = load_system(def_dir)

        # Generate and save the diagram
        save_mermaid_diagram(system, output)

        print(f"✓ Diagram generated: {output}")
        print()

        # Print some statistics
        print("System summary:")
        print(f"  Commands:   {len(system.commands)}")
        print(f"  Events:     {len(system.events)}")
        print(f"  Queries:    {len(system.queries)}")
        print(f"  Mutators:   {len(system.mutators)}")
        print(f"  Procedures: {len(system.procedures)}")
        print(f"  Policies:   {len(system.policies)}")
        print()
        print("✨ Done")

    except Exception as e:
        print(f"✗ Error generating diagram: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
