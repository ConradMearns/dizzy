"""Feat file loader — YAML ingestion, Pydantic validation, and cross-reference checks."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from dizzy.feat_schema import (
    CommandDef,
    EventDef,
    FeatureDefinition as PydanticFeatureDefinition,
    ModelDef,
    PolicyDef,
    ProcedureDef,
    ProjectionDef,
    QueryDef,
)


@dataclass
class FeatureDefinition:
    """Dict-keyed wrapper around the validated Pydantic schema.

    Generators and the CLI iterate collections by name, so we store each
    section as ``dict[str, XxxDef]`` keyed on the ``name`` field.
    """

    description: str | None = None
    models: dict[str, ModelDef] = field(default_factory=dict)
    queries: dict[str, QueryDef] = field(default_factory=dict)
    commands: dict[str, CommandDef] = field(default_factory=dict)
    events: dict[str, EventDef] = field(default_factory=dict)
    procedures: dict[str, ProcedureDef] = field(default_factory=dict)
    policies: dict[str, PolicyDef] = field(default_factory=dict)
    projections: dict[str, ProjectionDef] = field(default_factory=dict)


def _normalize_section(raw: dict, section: str) -> None:
    """Mutate *raw* in-place so every entry in *section* is a dict with a ``name`` key."""
    if section not in raw or not isinstance(raw[section], dict):
        return
    normalised: list[dict] = []
    for key, value in raw[section].items():
        if isinstance(value, str):
            entry = {"name": key, "description": value}
        else:
            entry = {**value, "name": key}
        normalised.append(entry)
    raw[section] = normalised


_SECTIONS = ("models", "queries", "commands", "events", "procedures", "policies", "projections")


def _normalize(raw: dict) -> dict:
    """Convert the user-facing YAML dict-key format into the list format expected by Pydantic."""
    result = dict(raw)
    for section in _SECTIONS:
        _normalize_section(result, section)
    return result


def _to_dict(items: list | None) -> dict:
    """Convert a list of Pydantic models (each with a ``name`` field) to a name-keyed dict."""
    if not items:
        return {}
    return {item.name: item for item in items}


def load_feat(path: str | Path) -> FeatureDefinition:
    """Load a ``.feat.yaml`` file, validate it, and return a dict-keyed FeatureDefinition."""
    raw = yaml.safe_load(Path(path).read_text())
    normalised = _normalize(raw)
    validated = PydanticFeatureDefinition.model_validate(normalised)
    return FeatureDefinition(
        description=validated.description,
        models=_to_dict(validated.models),
        queries=_to_dict(validated.queries),
        commands=_to_dict(validated.commands),
        events=_to_dict(validated.events),
        procedures=_to_dict(validated.procedures),
        policies=_to_dict(validated.policies),
        projections=_to_dict(validated.projections),
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
        for q in (proc.queries or []):
            if q not in feat.queries:
                errors.append(
                    f"procedure '{proc_name}': query '{q}' not declared in queries"
                )
        for e in (proc.emits or []):
            if e not in feat.events:
                errors.append(
                    f"procedure '{proc_name}': emits '{e}' not declared in events"
                )

    for policy_name, policy in feat.policies.items():
        if policy.event not in feat.events:
            errors.append(
                f"policy '{policy_name}': event '{policy.event}' not declared in events"
            )
        for e in (policy.emits or []):
            if e not in feat.commands:
                errors.append(
                    f"policy '{policy_name}': emits '{e}' not declared in commands"
                )

    for proj_name, proj in feat.projections.items():
        if proj.event not in feat.events:
            errors.append(
                f"projection '{proj_name}': event '{proj.event}' not declared in events"
            )
        if proj.model is not None and proj.model not in feat.models:
            errors.append(
                f"projection '{proj_name}': model '{proj.model}' not declared in models"
            )

    for query_name, query in feat.queries.items():
        if query.model is not None and query.model not in feat.models:
            errors.append(
                f"query '{query_name}': model '{query.model}' not declared in models"
            )
        if query.model is not None and query.adapter is None:
            errors.append(f"query '{query_name}': model declared without adapter")
        if query.adapter is not None and query.model is None:
            errors.append(f"query '{query_name}': adapter declared without model")
        if (
            query.model is not None
            and query.adapter is not None
            and query.model in feat.models
            and query.adapter not in (feat.models[query.model].adapters or [])
        ):
            errors.append(
                f"query '{query_name}': adapter '{query.adapter}' not declared on model '{query.model}'"
            )

    for proj_name, proj in feat.projections.items():
        if proj.model is not None and proj.adapter is None:
            errors.append(f"projection '{proj_name}': model declared without adapter")
        if proj.adapter is not None and proj.model is None:
            errors.append(f"projection '{proj_name}': adapter declared without model")
        if (
            proj.model is not None
            and proj.adapter is not None
            and proj.model in feat.models
            and proj.adapter not in (feat.models[proj.model].adapters or [])
        ):
            errors.append(
                f"projection '{proj_name}': adapter '{proj.adapter}' not declared on model '{proj.model}'"
            )

    return errors
