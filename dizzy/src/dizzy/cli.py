"""Dizzy — feature file generator CLI."""

from pathlib import Path
import typer

from dizzy.feat_loader import load_feat, validate_feat
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
from dizzy.generators.adapters import write_adapter
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
        write_scaffold_commands(feat.commands, output_dir)

    if feat.events:
        write_scaffold_events(feat.events, output_dir)

    for query in feat.queries or []:
        write_scaffold_query(query, output_dir)

    for model in feat.models or []:
        write_scaffold_model(model, output_dir)

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
    for query in feat.queries or []:
        stub = output_dir / "def" / "queries" / f"{query.name}.yaml"
        if not stub.exists():
            missing.append(f"def/queries/{query.name}.yaml")
    for model in feat.models or []:
        stub = output_dir / "def" / "models" / f"{model.name}.yaml"
        if not stub.exists():
            missing.append(f"def/models/{model.name}.yaml")

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

    for query in feat.queries or []:
        run_linkml_pydantic(
            output_dir / "def" / "queries" / f"{query.name}.yaml",
            output_dir / "gen_def" / "pydantic" / "query" / f"{query.name}.py",
        )

    for model in feat.models or []:
        run_linkml_pydantic(
            output_dir / "def" / "models" / f"{model.name}.yaml",
            output_dir / "gen_def" / "pydantic" / "models" / f"{model.name}.py",
        )
        if "sqla" in (model.adapters or []):
            run_linkml_sqla(
                output_dir / "def" / "models" / f"{model.name}.yaml",
                output_dir / "gen_def" / "sqla" / "models" / f"{model.name}.py",
            )

    # Step 2 — generate adapter classes
    unique_adapters: set[str] = set()
    for model in feat.models or []:
        unique_adapters.update(model.adapters or [])
    for adapter_name in unique_adapters:
        write_adapter(adapter_name, output_dir)

    # Step 3 — generate gen_int/ Protocol files from feat structure
    for query in feat.queries or []:
        write_gen_query_protocol(query, output_dir)

    for proc in feat.procedures or []:
        write_procedure_context(proc, output_dir)
        write_procedure_protocol(proc, output_dir)

    for policy in feat.policies or []:
        write_policy_context(policy, output_dir)
        write_policy_protocol(policy, output_dir)

    for proj in feat.projections or []:
        write_projection(proj, output_dir)

    # Step 4 — generate src/ stubs (skip if already exists)
    for query in feat.queries or []:
        write_src_query_stub(query.name, output_dir)

    for proc in feat.procedures or []:
        write_procedure_src_stub(proc, output_dir)

    for policy in feat.policies or []:
        write_policy_src_stub(policy, output_dir)

    for proj in feat.projections or []:
        write_projection_src_stub(proj, output_dir)

    # Step 5 — write __init__.py in every generated directory
    write_init_files(output_dir)

    typer.echo("Generated interfaces and source stubs. Next steps:")
    typer.echo("  Implement the src/ files to complete your feature.")


@app.command()
def docs() -> None:
    """Print Dizzy reference documentation for AI/LLM agents."""
    from importlib.resources import files

    content = files("dizzy").joinpath("docs_content.md").read_text()
    typer.echo(content)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
