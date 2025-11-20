"""CLI for dizzy code generation."""

import argparse
import sys
from pathlib import Path
import subprocess

from dizzy.utils.generate_query_interfaces import generate_query_interfaces
from dizzy.utils.generate_mutation_interfaces import generate_mutation_interfaces
from dizzy.utils.generate_procedure_contexts import generate_procedure_contexts
from dizzy.utils.generate_policy_contexts import generate_policy_contexts
from dizzy.utils.fix_event_types import fix_event_types, fix_command_types, fix_mutation_types


# Define all generation steps declaratively
GENERATORS = [
    {
        "name": "Query interfaces",
        "schema": "queries.yaml",
        "output": "query_interfaces.py",
        "func": generate_query_interfaces,
        "extra_args": {"gen_import_path": "gen.queries"}
    },
    {
        "name": "Mutation interfaces",
        "schema": "mutations.yaml",
        "output": "mutation_interfaces.py",
        "func": generate_mutation_interfaces,
        "extra_args": {"gen_import_path": "gen.mutations"}
    },
    {
        "name": "Procedure contexts",
        "schema": "procedures.d.yaml",
        "output": ["procedures.py", "procedure_interfaces.py"],
        "func": generate_procedure_contexts,
    },
    {
        "name": "Policy contexts",
        "schema": "policies.d.yaml",
        "output": ["policies.py", "policy_interfaces.py"],
        "func": generate_policy_contexts,
    },
]


def run_gen_pydantic(schema_file: Path, output_file: Path):
    """Run gen-pydantic to generate Pydantic models from LinkML schema."""
    result = subprocess.run(
        ["gen-pydantic", str(schema_file)],
        capture_output=True,
        text=True,
        check=True
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(result.stdout)

    print(f"✓ {output_file.name}")


def gen(def_dir: Path, gen_dir: Path):
    """Generate code from LinkML schemas."""
    def_dir = def_dir.resolve()
    gen_dir = gen_dir.resolve()

    if not def_dir.exists():
        print(f"✗ def/ directory not found at {def_dir}")
        sys.exit(1)

    print(f"Generating from {def_dir}/ to {gen_dir}/\n")

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
            run_gen_pydantic(schema_file, output_file)

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

    # Run all generators
    for generator in GENERATORS:
        schema_file = def_dir / generator["schema"]
        if not schema_file.exists():
            continue

        print(f"\n{generator['name']}:")

        # Handle single or multiple outputs
        outputs = generator["output"]
        if isinstance(outputs, str):
            outputs = [outputs]
        output_paths = [gen_dir / output for output in outputs]

        # Call generator with extra args if provided
        extra_args = generator.get("extra_args", {})
        generator["func"](schema_file, *output_paths, **extra_args)

    print("\n✨ Done")


def main():
    parser = argparse.ArgumentParser(description="Generate code from LinkML schemas")
    parser.add_argument("def_dir", type=Path, help="Directory containing LinkML schema files")
    parser.add_argument("gen_dir", type=Path, help="Output directory for all generated code")

    args = parser.parse_args()
    gen(args.def_dir, args.gen_dir)


if __name__ == "__main__":
    main()
