"""CLI for dizzy code generation."""

import typer
from pathlib import Path
from typing import Optional
import subprocess

from dizzy.utils.generate_query_interfaces import generate_query_interfaces
from dizzy.utils.generate_mutation_interfaces import generate_mutation_interfaces
from dizzy.utils.generate_procedure_contexts import generate_procedure_contexts
from dizzy.utils.fix_event_types import fix_event_types

app = typer.Typer()


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
    models_file = gen_dir / "models.py"
    if events_file.exists():
        if fix_event_types(events_file, models_file):
            print("✓ Fixed event type annotations")
        else:
            print("  No fixes needed for events.py")

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
    
    print()
    if success:
        print("✨ Done")
        raise typer.Exit(0)
    else:
        print("⚠️  Completed with errors")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
