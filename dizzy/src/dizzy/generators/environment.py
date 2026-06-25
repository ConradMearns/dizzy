"""Environment generator — scaffold def/environment.yaml.

Each environment entry names an injected constant/variable (acquired in place
of an os environment variable). Its shape is authored as one LinkML class.
"""

from pathlib import Path

from dizzy.feat_schema import EnvironmentDef
from dizzy.generators.yaml_util import description_lines
from dizzy.logger import logger


def render_scaffold_environment(environment: list[EnvironmentDef]) -> str:
    """Render a LinkML stub for def/environment.yaml from the feat definition."""
    lines = [
        "id: https://example.org/environment",
        "name: environment",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
    ]
    for env in environment:
        lines.append(f"  {env.name}:")
        lines.extend(description_lines(env.description, "    "))
        lines.append("    attributes: {}")
    lines.append("")
    return "\n".join(lines)


def write_scaffold_environment(environment: list[EnvironmentDef], output_dir: Path) -> None:
    """Write def/environment.yaml; skip if file already exists."""
    dest = output_dir / "def" / "environment.yaml"
    if dest.exists():
        logger.debug("skipped existing file", extra={"path": str(dest)})
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_environment(environment))
    logger.debug("wrote file", extra={"path": str(dest)})
