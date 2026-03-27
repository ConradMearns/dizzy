"""Projections generator — gen_int/python/projection/ combined context+protocol."""

from pathlib import Path

from dizzy.feat import FeatureDefinition


def _adapter_class_name(adapter_name: str) -> str:
    """Convert snake_case adapter identifier to PascalCase + Adapter suffix."""
    return "".join(word.capitalize() for word in adapter_name.split("_")) + "Adapter"


def render_projection(projection_name: str, feat: FeatureDefinition) -> str:
    """Render gen_int/python/projection/<projection_name>_projection.py."""
    projection = feat.projections[projection_name]
    context_class = f"{projection_name}_context"
    protocol_class = f"{projection_name}_projection"
    description = projection.description.strip()

    adapter_import = ""
    if projection.adapter is not None:
        adapter_cls = _adapter_class_name(projection.adapter)
        adapter_import = (
            f"from gen_int.python.adapters.{projection.adapter} import {adapter_cls}"
        )
        context_body = [f"    adapter: {adapter_cls}"]
    else:
        context_body = ["    pass"]

    imports = [
        "# AUTO-GENERATED — do not edit",
        "from dataclasses import dataclass",
        "from typing import Protocol",
        "",
        f"from gen_def.pydantic.events import {projection.event}",
    ]
    if adapter_import:
        imports.append(adapter_import)

    lines = imports + [
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
        f"    def __call__(self, event: {projection.event}, context: {context_class}) -> None:",
        '        """Apply the projection — mutate model state in response to the event."""',
        "        ...",
        "",
    ]
    return "\n".join(lines)


def write_projection(
    projection_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write gen_int/python/projection/<projection_name>_projection.py (always overwritten)."""
    dest = (
        output_dir
        / "gen_int"
        / "python"
        / "projection"
        / f"{projection_name}_projection.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_projection(projection_name, feat))


def render_src_projection_stub(projection_name: str, feat: FeatureDefinition) -> str:
    """Render a src/projection/<projection_name>.py implementation stub."""
    projection = feat.projections[projection_name]
    context_class = f"{projection_name}_context"
    protocol_class = f"{projection_name}_projection"
    lines = [
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.projection.{projection_name}_projection import {protocol_class}",
        f"from gen_int.python.projection.{projection_name}_projection import {context_class}",
        f"from gen_def.pydantic.events import {projection.event}",
        "",
        "",
        f"def {projection_name}(",
        f"    event: {projection.event},",
        f"    context: {context_class},",
        ") -> None:",
        "    raise NotImplementedError",
        "",
    ]
    return "\n".join(lines)


def write_projection_src_stub(
    projection_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write src/projection/<projection_name>.py; skip if file already exists."""
    dest = output_dir / "src" / "projection" / f"{projection_name}.py"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_src_projection_stub(projection_name, feat))
