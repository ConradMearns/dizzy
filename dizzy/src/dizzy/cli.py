"""Dizzy — feature file generator CLI."""

from pathlib import Path
import typer

from dizzy.feat import load_feat, validate_feat
from dizzy.generators.commands import write_scaffold_commands
from dizzy.generators.events import write_scaffold_events
from dizzy.generators.queries import (
    write_scaffold_query,
    write_gen_query_protocol,
    write_src_query_stub,
)
from dizzy.generators.models import write_scaffold_model
from dizzy.generators.procedures import (
    write_procedure_context,
    write_procedure_protocol,
    write_procedure_src_stub,
)
from dizzy.generators.policies import (
    write_policy_context,
    write_policy_protocol,
    write_policy_src_stub,
)
from dizzy.generators.projections import write_projection, write_projection_src_stub
from dizzy.generators.linkml_runner import run_linkml_pydantic, run_linkml_sqla
from dizzy.generators.init_emitter import write_init_files

app = typer.Typer()


@app.command("def")
def def_cmd(
    feat_file: Path = typer.Argument(..., help="Path to the .feat.yaml file"),
    output_dir: Path = typer.Argument(..., help="Output directory for generated files"),
) -> None:
    """Generate def/ stub files from a .feat.yaml feature definition."""
    feat = load_feat(feat_file)

    errors = validate_feat(feat)
    if errors:
        for err in errors:
            typer.echo(f"Error: {err}")
        raise typer.Exit(code=1)

    if feat.commands:
        write_scaffold_commands(feat, output_dir)

    if feat.events:
        write_scaffold_events(feat, output_dir)

    for query_name in feat.queries:
        write_scaffold_query(query_name, feat, output_dir)

    for schema_name in feat.models:
        write_scaffold_model(schema_name, feat, output_dir)

    typer.echo("Generated def/ stubs. Next steps:")
    typer.echo("  1. Fill in class definitions in def/models/*.yaml")
    typer.echo("  2. Add input/output shapes in def/queries/*.yaml")
    typer.echo("  3. Add attributes to def/commands.yaml and def/events.yaml")
    typer.echo("  4. Run: dizzy gen <feat_file> <output_dir>")


@app.command()
def gen(
    feat_file: Path = typer.Argument(..., help="Path to the .feat.yaml file"),
    output_dir: Path = typer.Argument(..., help="Output directory for generated files"),
) -> None:
    """Generate gen_def/, gen_int/, and src/ from an authored def/ directory."""
    feat = load_feat(feat_file)

    errors = validate_feat(feat)
    if errors:
        for err in errors:
            typer.echo(f"Error: {err}")
        raise typer.Exit(code=1)

    # Guard: check that all required def/ stubs exist before proceeding
    missing: list[str] = []
    if feat.commands and not (output_dir / "def" / "commands.yaml").exists():
        missing.append("def/commands.yaml")
    if feat.events and not (output_dir / "def" / "events.yaml").exists():
        missing.append("def/events.yaml")
    for query_name in feat.queries:
        stub = output_dir / "def" / "queries" / f"{query_name}.yaml"
        if not stub.exists():
            missing.append(f"def/queries/{query_name}.yaml")
    for schema_name in feat.models:
        stub = output_dir / "def" / "models" / f"{schema_name}.yaml"
        if not stub.exists():
            missing.append(f"def/models/{schema_name}.yaml")

    if missing:
        typer.echo(
            "Error: def/ stubs not found. Run `dizzy def <feat_file> <output_dir>` first."
        )
        typer.echo("Missing:")
        for path in missing:
            typer.echo(f"  {path}")
        raise typer.Exit(code=1)

    # Step 1 — run LinkML toolchain on def/ stubs → gen_def/
    if feat.commands:
        run_linkml_pydantic(
            output_dir / "def" / "commands.yaml",
            output_dir / "gen_def" / "pydantic" / "commands.py",
        )

    if feat.events:
        run_linkml_pydantic(
            output_dir / "def" / "events.yaml",
            output_dir / "gen_def" / "pydantic" / "events.py",
        )

    for query_name in feat.queries:
        run_linkml_pydantic(
            output_dir / "def" / "queries" / f"{query_name}.yaml",
            output_dir / "gen_def" / "pydantic" / "query" / f"{query_name}.py",
        )

    for schema_name in feat.models:
        run_linkml_pydantic(
            output_dir / "def" / "models" / f"{schema_name}.yaml",
            output_dir / "gen_def" / "pydantic" / "models" / f"{schema_name}.py",
        )
        run_linkml_sqla(
            output_dir / "def" / "models" / f"{schema_name}.yaml",
            output_dir / "gen_def" / "sqla" / "models" / f"{schema_name}.py",
        )

    # Step 2 — generate gen_int/ Protocol files from feat structure
    for query_name in feat.queries:
        write_gen_query_protocol(query_name, feat, output_dir)

    for procedure_name in feat.procedures:
        write_procedure_context(procedure_name, feat, output_dir)
        write_procedure_protocol(procedure_name, feat, output_dir)

    for policy_name in feat.policies:
        write_policy_context(policy_name, feat, output_dir)
        write_policy_protocol(policy_name, feat, output_dir)

    for projection_name in feat.projections:
        write_projection(projection_name, feat, output_dir)

    # Step 3 — generate src/ stubs (skip if already exists)
    for query_name in feat.queries:
        write_src_query_stub(query_name, output_dir)

    for procedure_name in feat.procedures:
        write_procedure_src_stub(procedure_name, feat, output_dir)

    for policy_name in feat.policies:
        write_policy_src_stub(policy_name, feat, output_dir)

    for projection_name in feat.projections:
        write_projection_src_stub(projection_name, feat, output_dir)

    # Step 4 — write __init__.py in every generated directory
    write_init_files(output_dir)

    typer.echo("Generated interfaces and source stubs. Next steps:")
    typer.echo("  Implement the src/ files to complete your feature.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
