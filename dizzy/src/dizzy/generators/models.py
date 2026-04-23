"""Models generator — scaffold def/models/ stubs."""

from pathlib import Path

from dizzy.feat_schema import ModelDef
from dizzy.logger import logger


def render_scaffold_model(model: ModelDef) -> str:
    """Render a minimal LinkML stub for def/models/<model.name>.yaml."""
    lines = [
        f"id: https://example.org/models/{model.name}",
        f"name: {model.name}",
        f"description: {model.description}",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes: {}",
        "",
    ]
    return "\n".join(lines)


def write_scaffold_model(model: ModelDef, output_dir: Path) -> None:
    """Write def/models/<model.name>.yaml; skip if file already exists."""
    dest = output_dir / "def" / "models" / f"{model.name}.yaml"
    if dest.exists():
        logger.debug("skipped existing file", extra={"path": str(dest)})
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_model(model))
    logger.debug("wrote file", extra={"path": str(dest)})
