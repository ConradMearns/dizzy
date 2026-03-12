"""Queries generator — scaffold def/queries/ stubs and gen_int/python/query/ protocols."""

from pathlib import Path

from dizzy.feat import FeatureDefinition


def render_scaffold_query_input(query_name: str, feat: FeatureDefinition) -> str:
    """Render a LinkML stub for def/queries/<query_name>_input.yaml."""
    query = feat.queries[query_name]
    class_name = f"{query_name}_input"
    lines = [
        f"id: https://example.org/queries/{class_name}",
        f"name: {class_name}",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
        f"  {class_name}:",
        f"    description: Input for {query_name} — {query.description}",
        "    attributes: {}",
        "",
    ]
    return "\n".join(lines)


def write_scaffold_query_input(
    query_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write def/queries/<query_name>_input.yaml; skip if file already exists."""
    dest = output_dir / "def" / "queries" / f"{query_name}_input.yaml"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_query_input(query_name, feat))


def render_scaffold_query_output(query_name: str, feat: FeatureDefinition) -> str:
    """Render a LinkML stub for def/queries/<query_name>_output.yaml."""
    query = feat.queries[query_name]
    class_name = f"{query_name}_output"
    lines = [
        f"id: https://example.org/queries/{class_name}",
        f"name: {class_name}",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
        f"  {class_name}:",
        f"    description: Output for {query_name} — {query.description}",
        "    attributes: {}",
        "",
    ]
    return "\n".join(lines)


def write_scaffold_query_output(
    query_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write def/queries/<query_name>_output.yaml; skip if file already exists."""
    dest = output_dir / "def" / "queries" / f"{query_name}_output.yaml"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_query_output(query_name, feat))


def render_gen_query_pydantic_stub(query_name: str, suffix: str, description: str) -> str:
    """Render a minimal Pydantic stub for a query input or output class."""
    class_name = f"{query_name}_{suffix}"
    lines = [
        "# AUTO-GENERATED — do not edit",
        "from pydantic import BaseModel",
        "",
        "",
        f"class {class_name}(BaseModel):",
        f'    """{description}"""',
        "    pass",
        "",
    ]
    return "\n".join(lines)


def write_gen_query_pydantic_input(
    query_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write gen_def/pydantic/query/<query_name>_input.py (always overwritten)."""
    query = feat.queries[query_name]
    dest = output_dir / "gen_def" / "pydantic" / "query" / f"{query_name}_input.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        render_gen_query_pydantic_stub(query_name, "input", query.description)
    )


def write_gen_query_pydantic_output(
    query_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write gen_def/pydantic/query/<query_name>_output.py (always overwritten)."""
    query = feat.queries[query_name]
    dest = output_dir / "gen_def" / "pydantic" / "query" / f"{query_name}_output.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        render_gen_query_pydantic_stub(query_name, "output", query.description)
    )


def render_gen_query_protocol(query_name: str, feat: FeatureDefinition) -> str:
    """Render gen_int/python/query/<query_name>.py — Protocol + context dataclass."""
    query = feat.queries[query_name]
    input_class = f"{query_name}_input"
    output_class = f"{query_name}_output"
    context_class = f"{query_name}_context"
    protocol_class = f"{query_name}_query"

    lines = [
        "# AUTO-GENERATED — do not edit",
        "from dataclasses import dataclass",
        "from typing import Protocol, Any",
        "",
        f"from gen_def.pydantic.query.{input_class} import {input_class}",
        f"from gen_def.pydantic.query.{output_class} import {output_class}",
        "",
        "",
        f"@dataclass",
        f"class {context_class}:",
        '    """SQLAlchemy session for the schema read by this query."""',
        f"    {query.model}: Any  # SQLAlchemy session for the {query.model} schema",
        "",
        "",
        f"class {protocol_class}(Protocol):",
        f'    """{query.description}"""',
        "",
        "    def __call__(",
        f"        self, input: {input_class}, context: {context_class}",
        f"    ) -> {output_class}:",
        "        ...",
        "",
    ]
    return "\n".join(lines)


def write_gen_query_protocol(
    query_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write gen_int/python/query/<query_name>.py (always overwritten)."""
    dest = output_dir / "gen_int" / "python" / "query" / f"{query_name}.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_gen_query_protocol(query_name, feat))


def render_src_query_stub(query_name: str) -> str:
    """Render a src/query/<query_name>.py implementation stub."""
    protocol_class = f"{query_name}_query"
    context_class = f"{query_name}_context"
    input_class = f"{query_name}_input"
    output_class = f"{query_name}_output"
    lines = [
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.query.{query_name} import {protocol_class}, {context_class}",
        f"from gen_def.pydantic.query.{query_name}_input import {input_class}",
        f"from gen_def.pydantic.query.{query_name}_output import {output_class}",
        "",
        "",
        f"def {query_name}(input: {input_class}, context: {context_class}) -> {output_class}:",
        "    raise NotImplementedError",
        "",
    ]
    return "\n".join(lines)


def write_src_query_stub(
    query_name: str, output_dir: Path
) -> None:
    """Write src/query/<query_name>.py; skip if file already exists."""
    dest = output_dir / "src" / "query" / f"{query_name}.py"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_src_query_stub(query_name))
