"""Feat file data model and loader."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AttributeDef:
    type: str
    required: bool = False


@dataclass
class CommandDef:
    description: str
    attributes: dict[str, AttributeDef] = field(default_factory=dict)


@dataclass
class EventDef:
    description: str
    attributes: dict[str, AttributeDef] = field(default_factory=dict)


@dataclass
class QueryDef:
    description: str
    model: str | None = None


@dataclass
class ProcedureDef:
    description: str
    command: str
    queries: list[str] = field(default_factory=list)
    emits: list[str] = field(default_factory=list)


@dataclass
class PolicyDef:
    description: str
    event: str
    emits: list[str] = field(default_factory=list)


@dataclass
class ProjectionDef:
    description: str
    event: str
    models: list[str] = field(default_factory=list)


@dataclass
class FeatureDefinition:
    description: str | None = None
    models: dict[str, str] = field(default_factory=dict)
    queries: dict[str, QueryDef] = field(default_factory=dict)
    commands: dict[str, CommandDef] = field(default_factory=dict)
    events: dict[str, EventDef] = field(default_factory=dict)
    procedures: dict[str, ProcedureDef] = field(default_factory=dict)
    policies: dict[str, PolicyDef] = field(default_factory=dict)
    projections: dict[str, ProjectionDef] = field(default_factory=dict)


def _parse_attribute_def(raw: dict[str, Any]) -> AttributeDef:
    return AttributeDef(
        type=raw["type"],
        required=bool(raw.get("required", False)),
    )


def _parse_command_def(raw: Any) -> CommandDef:
    if isinstance(raw, str):
        return CommandDef(description=raw)
    attrs = {
        name: _parse_attribute_def(val)
        for name, val in (raw.get("attributes") or {}).items()
    }
    return CommandDef(description=raw["description"], attributes=attrs)


def _parse_event_def(raw: Any) -> EventDef:
    if isinstance(raw, str):
        return EventDef(description=raw)
    attrs = {
        name: _parse_attribute_def(val)
        for name, val in (raw.get("attributes") or {}).items()
    }
    return EventDef(description=raw["description"], attributes=attrs)


def _parse_query_def(raw: Any) -> QueryDef:
    if isinstance(raw, str):
        raise ValueError("query entries must be a mapping with description and model")
    return QueryDef(description=raw["description"], model=raw.get("model"))


def _parse_procedure_def(raw: dict[str, Any]) -> ProcedureDef:
    return ProcedureDef(
        description=raw["description"],
        command=raw["command"],
        queries=list(raw.get("queries") or []),
        emits=list(raw.get("emits") or []),
    )


def _parse_policy_def(raw: dict[str, Any]) -> PolicyDef:
    return PolicyDef(
        description=raw["description"],
        event=raw["event"],
        emits=list(raw.get("emits") or []),
    )


def _parse_projection_def(raw: dict[str, Any]) -> ProjectionDef:
    return ProjectionDef(
        description=raw["description"],
        event=raw["event"],
        models=list(raw.get("models") or []),
    )


def validate_feat(feat: FeatureDefinition) -> list[str]:
    """Validate cross-references within a FeatureDefinition.

    Returns a list of error strings; empty list means the feat is valid.
    """
    errors: list[str] = []

    for proc_name, proc in feat.procedures.items():
        if proc.command not in feat.commands:
            errors.append(
                f"procedure '{proc_name}': command '{proc.command}' not declared in commands"
            )
        for q in proc.queries:
            if q not in feat.queries:
                errors.append(
                    f"procedure '{proc_name}': query '{q}' not declared in queries"
                )
        for e in proc.emits:
            if e not in feat.events:
                errors.append(
                    f"procedure '{proc_name}': emits '{e}' not declared in events"
                )

    for policy_name, policy in feat.policies.items():
        if policy.event not in feat.events:
            errors.append(
                f"policy '{policy_name}': event '{policy.event}' not declared in events"
            )
        for e in policy.emits:
            if e not in feat.commands:
                errors.append(
                    f"policy '{policy_name}': emits '{e}' not declared in commands"
                )

    for proj_name, proj in feat.projections.items():
        if proj.event not in feat.events:
            errors.append(
                f"projection '{proj_name}': event '{proj.event}' not declared in events"
            )
        for m in proj.models:
            if m not in feat.models:
                errors.append(
                    f"projection '{proj_name}': model '{m}' not declared in models"
                )

    for query_name, query in feat.queries.items():
        if query.model is not None and query.model not in feat.models:
            errors.append(
                f"query '{query_name}': model '{query.model}' not declared in models"
            )

    return errors


def load_feat(path: str | Path) -> FeatureDefinition:
    """Load and parse a .feat.yaml file into a FeatureDefinition."""
    raw = yaml.safe_load(Path(path).read_text())

    models = {
        name: desc
        for name, desc in (raw.get("models") or {}).items()
    }
    queries = {
        name: _parse_query_def(val)
        for name, val in (raw.get("queries") or {}).items()
    }
    commands = {
        name: _parse_command_def(val)
        for name, val in (raw.get("commands") or {}).items()
    }
    events = {
        name: _parse_event_def(val)
        for name, val in (raw.get("events") or {}).items()
    }
    procedures = {
        name: _parse_procedure_def(val)
        for name, val in (raw.get("procedures") or {}).items()
    }
    policies = {
        name: _parse_policy_def(val)
        for name, val in (raw.get("policies") or {}).items()
    }
    projections = {
        name: _parse_projection_def(val)
        for name, val in (raw.get("projections") or {}).items()
    }

    return FeatureDefinition(
        description=raw.get("description"),
        models=models,
        queries=queries,
        commands=commands,
        events=events,
        procedures=procedures,
        policies=policies,
        projections=projections,
    )
