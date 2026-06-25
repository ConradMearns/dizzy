"""Procedures generator — gen_int/python/procedure/ context and protocol."""

from pathlib import Path

from linkml_runtime.utils.formatutils import camelcase

from dizzy.feat_schema import ProcedureDef
from dizzy.generators.context_extras import render_context_extras
from dizzy.generators.paths import gen_int_root
from dizzy.logger import logger


def render_procedure_context(proc: ProcedureDef) -> str:
    """Render gen_int/python/procedure/<proc.name>_context.py."""
    emitters_class = f"{proc.name}_emitters"
    queries_class = f"{proc.name}_queries"
    context_class = f"{proc.name}_context"

    extras = render_context_extras(proc.name, proc.environment, proc.telemetry)

    lines = ["# AUTO-GENERATED — do not edit"]
    lines.append("from dataclasses import dataclass")
    if proc.emits or proc.queries or extras.needs_callable:
        lines.append("from typing import Callable")

    if proc.emits or proc.queries or extras.imports:
        lines.append("")
        for event_name in proc.emits or []:
            lines.append(f"from gen_def.pydantic.events import {camelcase(event_name)}")
        for query_name in proc.queries or []:
            lines.append(
                f"from gen_def.pydantic.query.{query_name} import "
                f"{camelcase(query_name)}Input, {camelcase(query_name)}Output"
            )
        lines.extend(extras.imports)

    # emitters dataclass
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {emitters_class}:")
    if proc.emits:
        for event_name in proc.emits:
            lines.append(f"    {event_name}: Callable[[{camelcase(event_name)}], None]")
    else:
        lines.append("    pass")

    # queries dataclass (only if there are queries)
    if proc.queries:
        lines.append("")
        lines.append("")
        lines.append("@dataclass")
        lines.append(f"class {queries_class}:")
        for query_name in proc.queries:
            # Host-bound query closure: the host injects the read adapter, so the
            # handler calls it with just the query input (symmetric with emit).
            lines.append(
                f"    {query_name}: Callable"
                f"[[{camelcase(query_name)}Input], {camelcase(query_name)}Output]"
            )

    # env / telemetry dataclasses
    lines.extend(extras.classes)

    # context dataclass
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {context_class}:")
    lines.append(f"    emit: {emitters_class}")
    if proc.queries:
        lines.append(f"    query: {queries_class}")
    lines.extend(extras.fields)

    lines.append("")
    return "\n".join(lines)


def write_procedure_context(proc: ProcedureDef, output_dir: Path) -> None:
    """Write gen_int/python/procedure/<proc.name>_context.py (always overwritten)."""
    dest = gen_int_root(output_dir) / "python" / "procedure" / f"{proc.name}_context.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_procedure_context(proc))
    logger.debug("wrote file", extra={"path": str(dest)})


def render_procedure_protocol(proc: ProcedureDef) -> str:
    """Render gen_int/python/procedure/<proc.name>_protocol.py."""
    context_class = f"{proc.name}_context"
    protocol_class = f"{proc.name}_protocol"
    command_class = camelcase(proc.command)
    description = (proc.description or "").strip()

    lines = [
        "# AUTO-GENERATED — do not edit",
        "from typing import Protocol",
        "",
        f"from gen_def.pydantic.commands import {command_class}",
        f"from gen_int.python.procedure.{proc.name}_context import (",
        f"    {context_class},",
        ")",
        "",
        "",
        f"class {protocol_class}(Protocol):",
        f'    """{description}"""',
        "",
        "    def __call__(",
        "        self,",
        f"        context: {context_class},",
        f"        command: {command_class},",
        "    ) -> None:",
        "        ...",
        "",
    ]
    return "\n".join(lines)


def write_procedure_protocol(proc: ProcedureDef, output_dir: Path) -> None:
    """Write gen_int/python/procedure/<proc.name>_protocol.py (always overwritten)."""
    dest = gen_int_root(output_dir) / "python" / "procedure" / f"{proc.name}_protocol.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_procedure_protocol(proc))
    logger.debug("wrote file", extra={"path": str(dest)})


def render_src_procedure_stub(proc: ProcedureDef) -> str:
    """Render a src/procedure/<proc.name>.py implementation stub."""
    context_class = f"{proc.name}_context"
    protocol_class = f"{proc.name}_protocol"
    command_class = camelcase(proc.command)
    lines = [
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.procedure.{proc.name}_protocol import {protocol_class}",
        f"from gen_int.python.procedure.{proc.name}_context import {context_class}",
        f"from gen_def.pydantic.commands import {command_class}",
        "",
        "",
        f"def {proc.name}(",
        f"    context: {context_class},",
        f"    command: {command_class},",
        ") -> None:",
        "    raise NotImplementedError",
        "",
    ]
    return "\n".join(lines)
