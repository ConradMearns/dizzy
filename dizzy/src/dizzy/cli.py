"""Dizzy — feature file generator CLI."""

from pathlib import Path
import typer

from dizzy.feat import load_feat
from dizzy.generators.commands import write_scaffold_commands
from dizzy.generators.events import write_scaffold_events
from dizzy.generators.queries import write_scaffold_query_input, write_scaffold_query_output
from dizzy.generators.models import write_scaffold_model

app = typer.Typer()


@app.command()
def scaffold(
    feat_file: Path = typer.Argument(..., help="Path to the .feat.yaml file"),
    output_dir: Path = typer.Argument(..., help="Output directory for generated files"),
) -> None:
    """Generate def/ stub files from a .feat.yaml feature definition."""
    feat = load_feat(feat_file)

    if feat.commands:
        write_scaffold_commands(feat, output_dir)

    if feat.events:
        write_scaffold_events(feat, output_dir)

    for query_name in feat.queries:
        write_scaffold_query_input(query_name, feat, output_dir)
        write_scaffold_query_output(query_name, feat, output_dir)

    for schema_name in feat.models:
        write_scaffold_model(schema_name, feat, output_dir)

    typer.echo("Scaffolded def/ stubs. Next steps:")
    typer.echo("  1. Fill in class definitions in def/models/*.yaml")
    typer.echo("  2. Add input/output shapes in def/queries/*.yaml")
    typer.echo("  3. Add attributes to def/commands.yaml and def/events.yaml")
    typer.echo("  4. Run: dizzy gen <feat_file> <output_dir>")


@app.command()
def gen(
    feat_file: Path = typer.Argument(..., help="Path to the .feat.yaml file"),
    output_dir: Path = typer.Argument(..., help="Output directory for generated files"),
) -> None:
    """Generate code from a .feat.yaml feature definition."""
    raise NotImplementedError


def main() -> None:
    app()


if __name__ == "__main__":
    main()
