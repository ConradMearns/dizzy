"""Events generator — scaffold def/events.yaml and gen_def/pydantic/events.py."""

from pathlib import Path

from dizzy.feat import FeatureDefinition

_LINKML_TYPE_MAP = {
    "string": "string",
    "integer": "integer",
    "boolean": "boolean",
    "float": "float",
}

_PYTHON_TYPE_MAP = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "float": "float",
}


def render_scaffold_events(feat: FeatureDefinition) -> str:
    """Render a LinkML stub for def/events.yaml from the feat definition."""
    lines = [
        "id: https://example.org/events",
        "name: events",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
    ]
    for name, evt in feat.events.items():
        lines.append(f"  {name}:")
        lines.append(f"    description: {evt.description}")
        if evt.attributes:
            lines.append("    attributes:")
            for attr_name, attr in evt.attributes.items():
                lines.append(f"      {attr_name}:")
                linkml_type = _LINKML_TYPE_MAP.get(attr.type, attr.type)
                lines.append(f"        range: {linkml_type}")
                if attr.required:
                    lines.append("        required: true")
        else:
            lines.append("    attributes: {}")
    lines.append("")
    return "\n".join(lines)


def write_scaffold_events(feat: FeatureDefinition, output_dir: Path) -> None:
    """Write def/events.yaml; skip if file already exists."""
    dest = output_dir / "def" / "events.yaml"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_events(feat))


def render_gen_events(feat: FeatureDefinition) -> str:
    """Render gen_def/pydantic/events.py from the feat definition."""
    needs_optional = any(
        not attr.required
        for evt in feat.events.values()
        for attr in evt.attributes.values()
    )

    lines = ["# AUTO-GENERATED — do not edit"]
    if needs_optional:
        lines.append("from typing import Optional")
        lines.append("")
    lines.append("from pydantic import BaseModel")

    for name, evt in feat.events.items():
        lines.append("")
        lines.append("")
        lines.append(f"class {name}(BaseModel):")
        lines.append(f'    """{evt.description}"""')
        if evt.attributes:
            for attr_name, attr in evt.attributes.items():
                py_type = _PYTHON_TYPE_MAP.get(attr.type, attr.type)
                if attr.required:
                    lines.append(f"    {attr_name}: {py_type}")
                else:
                    lines.append(f"    {attr_name}: Optional[{py_type}] = None")
        else:
            lines.append("    pass")

    lines.append("")
    return "\n".join(lines)


def write_gen_events(feat: FeatureDefinition, output_dir: Path) -> None:
    """Write gen_def/pydantic/events.py (always overwritten)."""
    dest = output_dir / "gen_def" / "pydantic" / "events.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_gen_events(feat))
