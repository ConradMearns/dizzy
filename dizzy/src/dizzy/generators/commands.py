"""Commands generator — scaffold def/commands.yaml."""

from pathlib import Path

from dizzy.feat_loader import FeatureDefinition

def render_scaffold_commands(feat: FeatureDefinition) -> str:
    """Render a LinkML stub for def/commands.yaml from the feat definition."""
    lines = [
        "id: https://example.org/commands",
        "name: commands",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
    ]
    for name, cmd in feat.commands.items():
        lines.append(f"  {name}:")
        lines.append(f"    description: {cmd.description}")
        lines.append("    attributes: {}")
    lines.append("")
    return "\n".join(lines)


def write_scaffold_commands(feat: FeatureDefinition, output_dir: Path) -> None:
    """Write def/commands.yaml; skip if file already exists."""
    dest = output_dir / "def" / "commands.yaml"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_commands(feat))


