"""Queries generator — scaffold def/queries/ stubs and gen_int/python/query/ protocols."""

from pathlib import Path

from dizzy.feat import FeatureDefinition


def _to_camel(snake: str) -> str:
    """Convert snake_case to CamelCase."""
    return "".join(word.capitalize() for word in snake.split("_"))


def render_scaffold_query(query_name: str, feat: FeatureDefinition) -> str:
    """Render a combined LinkML stub for def/queries/<query_name>.yaml."""
    query = feat.queries[query_name]
    camel = _to_camel(query_name)
    lines = [
        f"id: https://example.org/queries/{query_name}",
        f"name: {query_name}",
        f"description: {query.description}",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
        f"  {camel}Input:",
        f"    description: Input for {query_name}",
        "    attributes: {}",
        f"  {camel}Output:",
        f"    description: Output for {query_name}",
        "    attributes: {}",
        "",
    ]
    return "\n".join(lines)


def write_scaffold_query(
    query_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write def/queries/<query_name>.yaml; skip if file already exists."""
    dest = output_dir / "def" / "queries" / f"{query_name}.yaml"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_query(query_name, feat))


def render_gen_query_protocol(query_name: str, feat: FeatureDefinition) -> str:
    """Render gen_int/python/query/<query_name>.py — Protocol + context dataclass."""
    query = feat.queries[query_name]
    camel = _to_camel(query_name)
    input_class = f"{camel}Input"
    output_class = f"{camel}Output"
    context_class = f"{query_name}_context"
    protocol_class = f"{query_name}_query"

    if query.model is not None:
        context_body = [
            '    """SQLAlchemy session for the schema read by this query."""',
            f"    {query.model}: Any  # SQLAlchemy session for the {query.model} schema",
        ]
    else:
        context_body = [
            '    """No model dependency for this query."""',
            "    pass",
        ]

    lines = [
        "# AUTO-GENERATED — do not edit",
        "from dataclasses import dataclass",
        "from typing import Protocol, Any",
        "",
        f"from gen_def.pydantic.query.{query_name} import {input_class}, {output_class}",
        "",
        "",
        "@dataclass",
        f"class {context_class}:",
        *context_body,
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
    camel = _to_camel(query_name)
    input_class = f"{camel}Input"
    output_class = f"{camel}Output"
    protocol_class = f"{query_name}_query"
    context_class = f"{query_name}_context"
    lines = [
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.query.{query_name} import {protocol_class}, {context_class}",
        f"from gen_def.pydantic.query.{query_name} import {input_class}, {output_class}",
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
