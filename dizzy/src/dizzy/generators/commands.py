"""Commands generator — scaffold def/commands.yaml."""

from pathlib import Path

from dizzy.feat_schema import CommandDef
from dizzy.generators.yaml_util import description_lines
from dizzy.logger import logger


def render_scaffold_commands(commands: list[CommandDef]) -> str:
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
    for cmd in commands:
        lines.append(f"  {cmd.name}:")
        lines.extend(description_lines(cmd.description, "    "))
        lines.append("    attributes: {}")
    lines.append("")
    return "\n".join(lines)


def write_scaffold_commands(commands: list[CommandDef], output_dir: Path) -> None:
    """Write def/commands.yaml; skip if file already exists."""
    dest = output_dir / "def" / "commands.yaml"
    if dest.exists():
        logger.debug("skipped existing file", extra={"path": str(dest)})
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_commands(commands))
    logger.debug("wrote file", extra={"path": str(dest)})
