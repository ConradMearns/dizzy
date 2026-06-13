"""Policies generator — gen_int/python/policy/ context and protocol."""

from pathlib import Path

from linkml_runtime.utils.formatutils import camelcase

from dizzy.feat_schema import PolicyDef
from dizzy.generators.paths import gen_int_root
from dizzy.logger import logger


def render_policy_context(policy: PolicyDef) -> str:
    """Render gen_int/python/policy/<policy.name>_context.py."""
    emitters_class = f"{policy.name}_emitters"
    queries_class = f"{policy.name}_queries"
    context_class = f"{policy.name}_context"

    lines = ["# AUTO-GENERATED — do not edit"]
    lines.append("from dataclasses import dataclass")
    if policy.emits or policy.queries:
        lines.append("from typing import Callable")

    if policy.emits or policy.queries:
        lines.append("")
        for cmd_name in policy.emits:
            lines.append(f"from gen_def.pydantic.commands import {camelcase(cmd_name)}")
        for query_name in policy.queries or []:
            lines.append(
                f"from gen_def.pydantic.query.{query_name} import "
                f"{camelcase(query_name)}Input, {camelcase(query_name)}Output"
            )

    # emitters dataclass
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {emitters_class}:")
    if policy.emits:
        for cmd_name in policy.emits:
            lines.append(f"    {cmd_name}: Callable[[{camelcase(cmd_name)}], None]")
    else:
        lines.append("    pass")

    # queries dataclass (only if there are queries)
    if policy.queries:
        lines.append("")
        lines.append("")
        lines.append("@dataclass")
        lines.append(f"class {queries_class}:")
        for query_name in policy.queries or []:
            # Host-bound query closure: the host injects the read adapter, so the
            # policy calls it with just the query input (symmetric with emit).
            lines.append(
                f"    {query_name}: Callable"
                f"[[{camelcase(query_name)}Input], {camelcase(query_name)}Output]"
            )

    # context dataclass
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {context_class}:")
    lines.append(f"    emit: {emitters_class}")
    if policy.queries:
        lines.append(f"    query: {queries_class}")

    lines.append("")
    return "\n".join(lines)


def write_policy_context(policy: PolicyDef, output_dir: Path) -> None:
    """Write gen_int/python/policy/<policy.name>_context.py (always overwritten)."""
    dest = (
        gen_int_root(output_dir) / "python" / "policy" / f"{policy.name}_context.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_policy_context(policy))
    logger.debug("wrote file", extra={"path": str(dest)})


def render_policy_protocol(policy: PolicyDef) -> str:
    """Render gen_int/python/policy/<policy.name>_protocol.py."""
    context_class = f"{policy.name}_context"
    protocol_class = f"{policy.name}_protocol"
    event_class = camelcase(policy.event)
    description = policy.description.strip()

    lines = [
        "# AUTO-GENERATED — do not edit",
        "from typing import Protocol",
        "",
        f"from gen_def.pydantic.events import {event_class}",
        f"from gen_int.python.policy.{policy.name}_context import (",
        f"    {context_class},",
        ")",
        "",
        "",
        f"class {protocol_class}(Protocol):",
        f'    """{description}"""',
        "",
        "    def __call__(",
        "        self,",
        f"        event: {event_class},",
        f"        context: {context_class},",
        "    ) -> None:",
        "        ...",
        "",
    ]
    return "\n".join(lines)


def write_policy_protocol(policy: PolicyDef, output_dir: Path) -> None:
    """Write gen_int/python/policy/<policy.name>_protocol.py (always overwritten)."""
    dest = (
        gen_int_root(output_dir) / "python" / "policy" / f"{policy.name}_protocol.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_policy_protocol(policy))
    logger.debug("wrote file", extra={"path": str(dest)})


def render_src_policy_stub(policy: PolicyDef) -> str:
    """Render a src/policy/<policy.name>.py implementation stub."""
    context_class = f"{policy.name}_context"
    protocol_class = f"{policy.name}_protocol"
    event_class = camelcase(policy.event)
    lines = [
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.policy.{policy.name}_protocol import {protocol_class}",
        f"from gen_int.python.policy.{policy.name}_context import {context_class}",
        f"from gen_def.pydantic.events import {event_class}",
        "",
        "",
        f"def {policy.name}(",
        f"    event: {event_class},",
        f"    context: {context_class},",
        ") -> None:",
        "    raise NotImplementedError",
        "",
    ]
    return "\n".join(lines)
