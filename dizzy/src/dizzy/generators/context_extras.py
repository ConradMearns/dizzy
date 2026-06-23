"""Shared rendering for the optional environment + telemetry context fields.

Procedures, policies, projections, and queriers all build a context dataclass.
When a function declares ``environment`` and/or ``telemetry`` lists, those become
two extra dataclasses plus matching context fields:

  * ``env``       — injected constants, one field per entry typed by its
                    ``gen_def.pydantic.environment`` shape.
  * ``telemetry`` — host-injected observation sinks, one ``Callable`` field per
                    entry (the emitters pattern) typed by its payload shape.

Both are emitted only when the corresponding list is non-empty, so functions
that declare neither render byte-for-byte as before.
"""

from dataclasses import dataclass

from linkml_runtime.utils.formatutils import camelcase


@dataclass
class ContextExtras:
    """Rendered fragments to splice into a context module."""

    imports: list[str]
    """Import lines for the env/telemetry shapes (empty if none)."""
    classes: list[str]
    """Dataclass definition lines (env + telemetry), empty if none."""
    fields: list[str]
    """Context dataclass field lines (e.g. ``    env: foo_env``)."""
    needs_callable: bool
    """True when a telemetry sink requires ``typing.Callable``."""


def render_context_extras(
    name: str,
    environment: list[str] | None,
    telemetry: list[str] | None,
) -> ContextExtras:
    """Build the env/telemetry fragments for a function named *name*."""
    environment = environment or []
    telemetry = telemetry or []

    env_class = f"{name}_env"
    telemetry_class = f"{name}_telemetry"

    imports: list[str] = []
    classes: list[str] = []
    fields: list[str] = []

    for entry in environment:
        imports.append(
            f"from gen_def.pydantic.environment import {camelcase(entry)}"
        )
    for entry in telemetry:
        imports.append(
            f"from gen_def.pydantic.telemetry import {camelcase(entry)}"
        )

    if environment:
        classes.append("")
        classes.append("")
        classes.append("@dataclass")
        classes.append(f"class {env_class}:")
        for entry in environment:
            classes.append(f"    {entry}: {camelcase(entry)}")

    if telemetry:
        classes.append("")
        classes.append("")
        classes.append("@dataclass")
        classes.append(f"class {telemetry_class}:")
        for entry in telemetry:
            classes.append(f"    {entry}: Callable[[{camelcase(entry)}], None]")

    if environment:
        fields.append(f"    env: {env_class}")
    if telemetry:
        fields.append(f"    telemetry: {telemetry_class}")

    return ContextExtras(
        imports=imports,
        classes=classes,
        fields=fields,
        needs_callable=bool(telemetry),
    )
