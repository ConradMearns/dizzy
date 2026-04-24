"""Procedures generator — gen_int/python/procedure/ context and protocol."""

from pathlib import Path

from dizzy.feat_schema import ProcedureDef
from dizzy.logger import logger


def render_procedure_context(proc: ProcedureDef) -> str:
    """Render gen_int/python/procedure/<proc.name>_context.py."""
    emitters_class = f"{proc.name}_emitters"
    queries_class = f"{proc.name}_queries"
    context_class = f"{proc.name}_context"

    lines = ["# AUTO-GENERATED — do not edit"]
    lines.append("from dataclasses import dataclass")
    if proc.emits:
        lines.append("from typing import Callable")

    if proc.emits or proc.queries:
        lines.append("")
        for event_name in proc.emits:
            lines.append(f"from gen_def.pydantic.events import {event_name}")
        for query_name in proc.queries:
            lines.append(
                f"from gen_int.python.query.{query_name} import {query_name}_query"
            )

    # emitters dataclass
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {emitters_class}:")
    if proc.emits:
        for event_name in proc.emits:
            lines.append(f"    {event_name}: Callable[[{event_name}], None]")
    else:
        lines.append("    pass")

    # queries dataclass (only if there are queries)
    if proc.queries:
        lines.append("")
        lines.append("")
        lines.append("@dataclass")
        lines.append(f"class {queries_class}:")
        for query_name in proc.queries:
            lines.append(f"    {query_name}: {query_name}_query")

    # context dataclass
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {context_class}:")
    lines.append(f"    emit: {emitters_class}")
    if proc.queries:
        lines.append(f"    query: {queries_class}")

    lines.append("")
    return "\n".join(lines)


def write_procedure_context(proc: ProcedureDef, output_dir: Path) -> None:
    """Write gen_int/python/procedure/<proc.name>_context.py (always overwritten)."""
    dest = (
        output_dir
        / "gen_int"
        / "python"
        / "procedure"
        / f"{proc.name}_context.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_procedure_context(proc))
    logger.debug("wrote file", extra={"path": str(dest)})


def render_procedure_protocol(proc: ProcedureDef) -> str:
    """Render gen_int/python/procedure/<proc.name>_protocol.py."""
    context_class = f"{proc.name}_context"
    protocol_class = f"{proc.name}_protocol"
    description = proc.description.strip()

    lines = [
        "# AUTO-GENERATED — do not edit",
        "from typing import Protocol",
        "",
        f"from gen_def.pydantic.commands import {proc.command}",
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
        f"        command: {proc.command},",
        "    ) -> None:",
        "        ...",
        "",
    ]
    return "\n".join(lines)


def write_procedure_protocol(proc: ProcedureDef, output_dir: Path) -> None:
    """Write gen_int/python/procedure/<proc.name>_protocol.py (always overwritten)."""
    dest = (
        output_dir
        / "gen_int"
        / "python"
        / "procedure"
        / f"{proc.name}_protocol.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_procedure_protocol(proc))
    logger.debug("wrote file", extra={"path": str(dest)})


def render_src_procedure_stub(proc: ProcedureDef) -> str:
    """Render a src/procedure/<proc.name>.py implementation stub."""
    context_class = f"{proc.name}_context"
    protocol_class = f"{proc.name}_protocol"
    lines = [
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.procedure.{proc.name}_protocol import {protocol_class}",
        f"from gen_int.python.procedure.{proc.name}_context import {context_class}",
        f"from gen_def.pydantic.commands import {proc.command}",
        "",
        "",
        f"def {proc.name}(",
        f"    context: {context_class},",
        f"    command: {proc.command},",
        ") -> None:",
        "    raise NotImplementedError",
        "",
    ]
    return "\n".join(lines)


def write_procedure_src_stub(proc: ProcedureDef, output_dir: Path) -> None:
    """Write src/procedure/<proc.name>.py; skip if file already exists."""
    dest = output_dir / "src" / "procedure" / f"{proc.name}.py"
    if dest.exists():
        logger.debug("skipped existing file", extra={"path": str(dest)})
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_src_procedure_stub(proc))
    logger.debug("wrote file", extra={"path": str(dest)})
