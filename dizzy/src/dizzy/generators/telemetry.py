"""Telemetry generator — scaffold def/telemetry.yaml.

Each telemetry entry names a host-injected observation sink. Its LinkML class
describes the payload shape the function passes into the sink callable.
"""

from pathlib import Path

from dizzy.feat_schema import TelemetryDef
from dizzy.generators.yaml_util import description_lines
from dizzy.logger import logger


def render_scaffold_telemetry(telemetry: list[TelemetryDef]) -> str:
    """Render a LinkML stub for def/telemetry.yaml from the feat definition."""
    lines = [
        "id: https://example.org/telemetry",
        "name: telemetry",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
    ]
    for tel in telemetry:
        lines.append(f"  {tel.name}:")
        lines.extend(description_lines(tel.description, "    "))
        lines.append("    attributes: {}")
    lines.append("")
    return "\n".join(lines)


def write_scaffold_telemetry(telemetry: list[TelemetryDef], output_dir: Path) -> None:
    """Write def/telemetry.yaml; skip if file already exists."""
    dest = output_dir / "def" / "telemetry.yaml"
    if dest.exists():
        logger.debug("skipped existing file", extra={"path": str(dest)})
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_telemetry(telemetry))
    logger.debug("wrote file", extra={"path": str(dest)})
