"""Policies generator — gen_int/python/policy/ context and protocol."""

from pathlib import Path

from dizzy.feat import FeatureDefinition


def render_policy_context(policy_name: str, feat: FeatureDefinition) -> str:
    """Render gen_int/python/policy/<policy_name>_context.py."""
    policy = feat.policies[policy_name]
    emitters_class = f"{policy_name}_emitters"
    context_class = f"{policy_name}_context"

    lines = ["# AUTO-GENERATED — do not edit"]
    lines.append("from dataclasses import dataclass")
    if policy.emits:
        lines.append("from typing import Callable")
        lines.append("")
        for cmd_name in policy.emits:
            lines.append(f"from gen_def.pydantic.commands import {cmd_name}")

    # emitters dataclass
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {emitters_class}:")
    if policy.emits:
        for cmd_name in policy.emits:
            lines.append(f"    {cmd_name}: Callable[[{cmd_name}], None]")
    else:
        lines.append("    pass")

    # context dataclass
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {context_class}:")
    lines.append(f"    emit: {emitters_class}")

    lines.append("")
    return "\n".join(lines)


def write_policy_context(
    policy_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write gen_int/python/policy/<policy_name>_context.py (always overwritten)."""
    dest = (
        output_dir / "gen_int" / "python" / "policy" / f"{policy_name}_context.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_policy_context(policy_name, feat))


def render_policy_protocol(policy_name: str, feat: FeatureDefinition) -> str:
    """Render gen_int/python/policy/<policy_name>_protocol.py."""
    policy = feat.policies[policy_name]
    context_class = f"{policy_name}_context"
    protocol_class = f"{policy_name}_protocol"
    description = policy.description.strip()

    lines = [
        "# AUTO-GENERATED — do not edit",
        "from typing import Protocol",
        "",
        f"from gen_def.pydantic.events import {policy.event}",
        f"from gen_int.python.policy.{policy_name}_context import (",
        f"    {context_class},",
        ")",
        "",
        "",
        f"class {protocol_class}(Protocol):",
        f'    """{description}"""',
        "",
        "    def __call__(",
        "        self,",
        f"        event: {policy.event},",
        f"        context: {context_class},",
        "    ) -> None:",
        "        ...",
        "",
    ]
    return "\n".join(lines)


def write_policy_protocol(
    policy_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write gen_int/python/policy/<policy_name>_protocol.py (always overwritten)."""
    dest = (
        output_dir / "gen_int" / "python" / "policy" / f"{policy_name}_protocol.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_policy_protocol(policy_name, feat))


def render_src_policy_stub(policy_name: str, feat: FeatureDefinition) -> str:
    """Render a src/policy/<policy_name>.py implementation stub."""
    policy = feat.policies[policy_name]
    context_class = f"{policy_name}_context"
    protocol_class = f"{policy_name}_protocol"
    lines = [
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.policy.{policy_name}_protocol import {protocol_class}",
        f"from gen_int.python.policy.{policy_name}_context import {context_class}",
        f"from gen_def.pydantic.events import {policy.event}",
        "",
        "",
        f"def {policy_name}(",
        f"    event: {policy.event},",
        f"    context: {context_class},",
        ") -> None:",
        "    raise NotImplementedError",
        "",
    ]
    return "\n".join(lines)


def write_policy_src_stub(
    policy_name: str, feat: FeatureDefinition, output_dir: Path
) -> None:
    """Write src/policy/<policy_name>.py; skip if file already exists."""
    dest = output_dir / "src" / "policy" / f"{policy_name}.py"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_src_policy_stub(policy_name, feat))
