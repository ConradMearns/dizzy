"""Adapters generator — gen_int/python/adapters/ shared adapter classes."""

import warnings
from pathlib import Path

from dizzy.generators.paths import gen_int_root
from dizzy.logger import logger

_ADAPTER_REGISTRY: dict[str, dict[str, str]] = {
    "sqla": {
        "class_name": "SqlaAdapter",
        "field_name": "session",
        "field_type": "Session",
        "import_line": "from sqlalchemy.orm import Session",
        "docstring": "Adapter providing a SQLAlchemy session.",
    },
    "relative_filesystem": {
        "class_name": "RelativeFilesystemAdapter",
        "field_name": "root",
        "field_type": "Path",
        "import_line": "from pathlib import Path",
        "docstring": "Adapter providing a root path for relative filesystem access.",
    },
}


def render_adapter(adapter_name: str) -> str:
    """Render the source for a shared adapter dataclass."""
    if adapter_name not in _ADAPTER_REGISTRY:
        warnings.warn(f"Unknown adapter '{adapter_name}' — skipping generation", stacklevel=2)
        return ""

    info = _ADAPTER_REGISTRY[adapter_name]
    lines = [
        "# AUTO-GENERATED — do not edit",
        "from dataclasses import dataclass",
        info["import_line"],
        "",
        "",
        "@dataclass",
        f"class {info['class_name']}:",
        f'    """{info["docstring"]}"""',
        "",
        f"    {info['field_name']}: {info['field_type']}",
        "",
    ]
    return "\n".join(lines)


def write_adapter(adapter_name: str, output_dir: Path) -> None:
    """Write gen_int/python/adapters/<adapter_name>.py (always overwritten)."""
    source = render_adapter(adapter_name)
    if not source:
        return
    dest = gen_int_root(output_dir) / "python" / "adapters" / f"{adapter_name}.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(source)
    logger.debug("wrote file", extra={"path": str(dest)})
