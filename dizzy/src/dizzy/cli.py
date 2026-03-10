"""Dizzy — feature file generator CLI."""

from pathlib import Path
import typer

app = typer.Typer()


@app.command()
def gen(
    feat_file: Path = typer.Argument(..., help="Path to the .feat.yaml file"),
    output_dir: Path = typer.Argument(..., help="Output directory for generated files"),
):
    """Generate code from a .feat.yaml feature definition."""
    raise NotImplementedError


def main():
    app()


if __name__ == "__main__":
    main()
