"""Queries generator — scaffold def/queries/ stubs and gen_int/python/query/ protocols."""

from pathlib import Path

from dizzy.feat_schema import QueryDef
from dizzy.logger import logger


def _to_camel(snake: str) -> str:
    """Convert snake_case to CamelCase."""
    return "".join(word.capitalize() for word in snake.split("_"))


def render_scaffold_query(query: QueryDef) -> str:
    """Render a combined LinkML stub for def/queries/<query.name>.yaml."""
    camel = _to_camel(query.name)
    lines = [
        f"id: https://example.org/queries/{query.name}",
        f"name: {query.name}",
        f"description: {query.description}",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
        f"  {camel}Input:",
        f"    description: Input for {query.name}",
        "    attributes: {}",
        f"  {camel}Output:",
        f"    description: Output for {query.name}",
        "    attributes: {}",
        "",
    ]
    return "\n".join(lines)


def write_scaffold_query(query: QueryDef, output_dir: Path) -> None:
    """Write def/queries/<query.name>.yaml; skip if file already exists."""
    dest = output_dir / "def" / "queries" / f"{query.name}.yaml"
    if dest.exists():
        logger.debug("skipped existing file", extra={"path": str(dest)})
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_query(query))
    logger.debug("wrote file", extra={"path": str(dest)})


def _adapter_class_name(adapter_name: str) -> str:
    """Convert snake_case adapter identifier to PascalCase + Adapter suffix."""
    return "".join(word.capitalize() for word in adapter_name.split("_")) + "Adapter"


def render_gen_query_protocol(query: QueryDef) -> str:
    """Render gen_int/python/query/<query.name>.py — Protocol + context dataclass."""
    camel = _to_camel(query.name)
    input_class = f"{camel}Input"
    output_class = f"{camel}Output"
    context_class = f"{query.name}_context"
    protocol_class = f"{query.name}_query"

    adapter_import = ""
    if query.adapter is not None:
        adapter_cls = _adapter_class_name(query.adapter)
        adapter_import = (
            f"from gen_int.python.adapters.{query.adapter} import {adapter_cls}"
        )
        context_body = [f"    adapter: {adapter_cls}"]
    else:
        context_body = ["    pass"]

    imports = [
        "# AUTO-GENERATED — do not edit",
        "from dataclasses import dataclass",
        "from typing import Protocol",
        "",
        f"from gen_def.pydantic.query.{query.name} import {input_class}, {output_class}",
    ]
    if adapter_import:
        imports.append(adapter_import)

    lines = imports + [
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


def write_gen_query_protocol(query: QueryDef, output_dir: Path) -> None:
    """Write gen_int/python/query/<query.name>.py (always overwritten)."""
    dest = output_dir / "gen_int" / "python" / "query" / f"{query.name}.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_gen_query_protocol(query))
    logger.debug("wrote file", extra={"path": str(dest)})


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


def write_src_query_stub(query_name: str, output_dir: Path) -> None:
    """Write src/query/<query_name>.py; skip if file already exists."""
    dest = output_dir / "src" / "query" / f"{query_name}.py"
    if dest.exists():
        logger.debug("skipped existing file", extra={"path": str(dest)})
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_src_query_stub(query_name))
    logger.debug("wrote file", extra={"path": str(dest)})
