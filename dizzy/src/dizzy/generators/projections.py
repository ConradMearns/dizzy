"""Projections generator — gen_int/python/projection/ combined context+protocol."""

from pathlib import Path

from linkml_runtime.utils.formatutils import camelcase

from dizzy.feat_schema import ProjectionDef
from dizzy.generators.context_extras import render_context_extras
from dizzy.generators.paths import gen_int_root
from dizzy.logger import logger


def _adapter_class_name(adapter_name: str) -> str:
    """Convert snake_case adapter identifier to PascalCase + Adapter suffix."""
    return "".join(word.capitalize() for word in adapter_name.split("_")) + "Adapter"


def render_projection(proj: ProjectionDef) -> str:
    """Render gen_int/python/projection/<proj.name>_projection.py."""
    context_class = f"{proj.name}_context"
    protocol_class = f"{proj.name}_projection"
    event_class = camelcase(proj.event)
    description = proj.description.strip()

    extras = render_context_extras(proj.name, proj.environment, proj.telemetry)

    context_body: list[str] = []
    adapter_import = ""
    if proj.adapter is not None:
        adapter_cls = _adapter_class_name(proj.adapter)
        adapter_import = (
            f"from gen_int.python.adapters.{proj.adapter} import {adapter_cls}"
        )
        context_body.append(f"    adapter: {adapter_cls}")
    context_body.extend(extras.fields)
    if not context_body:
        context_body.append("    pass")

    imports = [
        "# AUTO-GENERATED — do not edit",
        "from dataclasses import dataclass",
        "from typing import Protocol",
    ]
    if extras.needs_callable:
        imports.append("from typing import Callable")
    imports += [
        "",
        f"from gen_def.pydantic.events import {event_class}",
    ]
    if adapter_import:
        imports.append(adapter_import)
    imports.extend(extras.imports)

    lines = imports + [
        *extras.classes,
        "",
        "",
        "@dataclass",
        f"class {context_class}:",
        *context_body,
    ]

    lines += [
        "",
        "",
        f"class {protocol_class}(Protocol):",
        f'    """{description}"""',
        "",
        f"    def __call__(self, event: {event_class}, context: {context_class}) -> None:",
        '        """Apply the projection — mutate model state in response to the event."""',
        "        ...",
        "",
    ]
    return "\n".join(lines)


def write_projection(proj: ProjectionDef, output_dir: Path) -> None:
    """Write gen_int/python/projection/<proj.name>_projection.py (always overwritten)."""
    dest = (
        gen_int_root(output_dir)
        / "python"
        / "projection"
        / f"{proj.name}_projection.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_projection(proj))
    logger.debug("wrote file", extra={"path": str(dest)})


def render_src_projection_stub(proj: ProjectionDef) -> str:
    """Render a src/projection/<proj.name>.py implementation stub."""
    context_class = f"{proj.name}_context"
    protocol_class = f"{proj.name}_projection"
    event_class = camelcase(proj.event)
    lines = [
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.projection.{proj.name}_projection import {protocol_class}",
        f"from gen_int.python.projection.{proj.name}_projection import {context_class}",
        f"from gen_def.pydantic.events import {event_class}",
        "",
        "",
        f"def {proj.name}(",
        f"    event: {event_class},",
        f"    context: {context_class},",
        ") -> None:",
        "    raise NotImplementedError",
        "",
    ]
    return "\n".join(lines)
