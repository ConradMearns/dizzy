"""Models generator — scaffold def/models/ and gen_def/pydantic/models/ + gen_def/sqla/models/."""

from pathlib import Path

import yaml

from dizzy.feat import FeatureDefinition

_RANGE_TO_PYTHON = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "float": "float",
}

_RANGE_TO_SQLA = {
    "string": "String",
    "integer": "Integer",
    "boolean": "Boolean",
    "float": "Float",
}


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


def _load_def_classes(schema_name: str, def_dir: Path) -> dict:
    """Load classes dict from def/models/<schema_name>.yaml."""
    def_file = def_dir / "def" / "models" / f"{schema_name}.yaml"
    if not def_file.exists():
        return {}
    raw = yaml.safe_load(def_file.read_text())
    return raw.get("classes") or {}


def render_gen_model_pydantic(schema_name: str, def_dir: Path) -> str:
    """Render gen_def/pydantic/models/<schema_name>.py from authored def file."""
    classes = _load_def_classes(schema_name, def_dir)

    needs_optional = any(
        not (attr_data or {}).get("required", False)
        for cls_data in classes.values()
        for attr_data in ((cls_data or {}).get("attributes") or {}).values()
    )

    lines = ["# AUTO-GENERATED — do not edit"]
    if needs_optional:
        lines.append("from typing import Optional")
        lines.append("")
    lines.append("from pydantic import BaseModel")

    for class_name, class_data in classes.items():
        lines.append("")
        lines.append("")
        lines.append(f"class {class_name}(BaseModel):")
        attributes = (class_data or {}).get("attributes") or {}
        if attributes:
            for attr_name, attr_data in attributes.items():
                attr_data = attr_data or {}
                range_type = attr_data.get("range", "string")
                py_type = _RANGE_TO_PYTHON.get(range_type, range_type)
                required = attr_data.get("required", False)
                if required:
                    lines.append(f"    {attr_name}: {py_type}")
                else:
                    lines.append(f"    {attr_name}: Optional[{py_type}] = None")
        else:
            lines.append("    pass")

    lines.append("")
    return "\n".join(lines)


def write_gen_model_pydantic(schema_name: str, def_dir: Path, output_dir: Path) -> None:
    """Write gen_def/pydantic/models/<schema_name>.py (always overwritten)."""
    dest = output_dir / "gen_def" / "pydantic" / "models" / f"{schema_name}.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_gen_model_pydantic(schema_name, def_dir))


def render_gen_model_sqla(schema_name: str, def_dir: Path) -> str:
    """Render gen_def/sqla/models/<schema_name>.py from authored def file."""
    classes = _load_def_classes(schema_name, def_dir)

    needs_optional = any(
        not (attr_data or {}).get("required", False)
        for cls_data in classes.values()
        for attr_data in ((cls_data or {}).get("attributes") or {}).values()
    )

    sqla_types_needed: set[str] = set()
    for cls_data in classes.values():
        for attr_data in ((cls_data or {}).get("attributes") or {}).values():
            range_type = (attr_data or {}).get("range", "string")
            sqla_type = _RANGE_TO_SQLA.get(range_type)
            if sqla_type:
                sqla_types_needed.add(sqla_type)
    sqla_types_str = ", ".join(sorted(sqla_types_needed)) if sqla_types_needed else "String"

    lines = ["# AUTO-GENERATED — do not edit"]
    if needs_optional:
        lines.append("from typing import Optional")
        lines.append("")
    lines.append("from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column")
    lines.append(f"from sqlalchemy import {sqla_types_str}")
    lines.append("")
    lines.append("")
    lines.append("class Base(DeclarativeBase):")
    lines.append("    pass")

    for class_name, class_data in classes.items():
        lines.append("")
        lines.append("")
        lines.append(f"class {class_name}(Base):")
        lines.append(f'    __tablename__ = "{class_name.lower()}"')
        lines.append("    id: Mapped[int] = mapped_column(primary_key=True)")
        attributes = (class_data or {}).get("attributes") or {}
        for attr_name, attr_data in attributes.items():
            attr_data = attr_data or {}
            range_type = attr_data.get("range", "string")
            py_type = _RANGE_TO_PYTHON.get(range_type, range_type)
            sqla_type = _RANGE_TO_SQLA.get(range_type, "String")
            required = attr_data.get("required", False)
            if required:
                lines.append(f"    {attr_name}: Mapped[{py_type}] = mapped_column({sqla_type})")
            else:
                lines.append(
                    f"    {attr_name}: Mapped[Optional[{py_type}]] = mapped_column({sqla_type}, nullable=True)"
                )

    lines.append("")
    return "\n".join(lines)


def write_gen_model_sqla(schema_name: str, def_dir: Path, output_dir: Path) -> None:
    """Write gen_def/sqla/models/<schema_name>.py (always overwritten)."""
    dest = output_dir / "gen_def" / "sqla" / "models" / f"{schema_name}.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_gen_model_sqla(schema_name, def_dir))
