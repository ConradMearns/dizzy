"""Models generator — scaffold def/models/ stubs."""

from pathlib import Path

from dizzy.feat import FeatureDefinition


def render_scaffold_model(schema_name: str, feat: FeatureDefinition) -> str:
    """Render a minimal LinkML stub for def/models/<schema_name>.yaml."""
    description = feat.models.get(schema_name, "")
    lines = [
        f"id: https://example.org/models/{schema_name}",
        f"name: {schema_name}",
        f"description: {description}",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes: {}",
        "",
    ]
    return "\n".join(lines)


def write_scaffold_model(schema_name: str, feat: FeatureDefinition, output_dir: Path) -> None:
    """Write def/models/<schema_name>.yaml; skip if file already exists."""
    dest = output_dir / "def" / "models" / f"{schema_name}.yaml"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_model(schema_name, feat))
