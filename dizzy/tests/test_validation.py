"""Tests for validate_feat cross-reference validation."""

import pytest

from dizzy.feat import (
    CommandDef,
    EventDef,
    FeatureDefinition,
    PolicyDef,
    ProcedureDef,
    ProjectionDef,
    QueryDef,
    validate_feat,
)


def test_valid_full_feat(recipe_feat):
    assert validate_feat(recipe_feat) == []


def test_valid_partial_feat(partial_feat):
    assert validate_feat(partial_feat) == []


def test_procedure_references_unknown_command():
    feat = FeatureDefinition(
        commands={"do_thing": CommandDef(description="does a thing")},
        procedures={
            "my_proc": ProcedureDef(description="proc", command="unknown_command")
        },
    )
    errors = validate_feat(feat)
    assert any("command 'unknown_command'" in e for e in errors)


def test_procedure_references_unknown_query():
    feat = FeatureDefinition(
        commands={"do_thing": CommandDef(description="does a thing")},
        queries={"real_query": QueryDef(description="real")},
        procedures={
            "my_proc": ProcedureDef(
                description="proc", command="do_thing", queries=["missing_query"]
            )
        },
    )
    errors = validate_feat(feat)
    assert any("query 'missing_query'" in e for e in errors)


def test_procedure_emits_unknown_event():
    feat = FeatureDefinition(
        commands={"do_thing": CommandDef(description="does a thing")},
        events={"real_event": EventDef(description="real")},
        procedures={
            "my_proc": ProcedureDef(
                description="proc", command="do_thing", emits=["ghost_event"]
            )
        },
    )
    errors = validate_feat(feat)
    assert any("emits 'ghost_event'" in e for e in errors)


def test_policy_references_unknown_event():
    feat = FeatureDefinition(
        events={"real_event": EventDef(description="real")},
        policies={
            "my_policy": PolicyDef(description="policy", event="unknown_event")
        },
    )
    errors = validate_feat(feat)
    assert any("event 'unknown_event'" in e for e in errors)


def test_policy_emits_unknown_command():
    feat = FeatureDefinition(
        commands={"real_cmd": CommandDef(description="real")},
        events={"some_event": EventDef(description="event")},
        policies={
            "my_policy": PolicyDef(
                description="policy", event="some_event", emits=["ghost_cmd"]
            )
        },
    )
    errors = validate_feat(feat)
    assert any("emits 'ghost_cmd'" in e for e in errors)


def test_projection_references_unknown_event():
    feat = FeatureDefinition(
        events={"real_event": EventDef(description="real")},
        projections={
            "my_proj": ProjectionDef(description="proj", event="unknown_event")
        },
    )
    errors = validate_feat(feat)
    assert any("event 'unknown_event'" in e for e in errors)


def test_projection_references_unknown_model():
    feat = FeatureDefinition(
        models={"real_model": "a real model"},
        events={"some_event": EventDef(description="event")},
        projections={
            "my_proj": ProjectionDef(
                description="proj", event="some_event", models=["ghost_model"]
            )
        },
    )
    errors = validate_feat(feat)
    assert any("model 'ghost_model'" in e for e in errors)


def test_query_references_unknown_model():
    feat = FeatureDefinition(
        models={"real_model": "a real model"},
        queries={"my_query": QueryDef(description="query", model="ghost_model")},
    )
    errors = validate_feat(feat)
    assert any("model 'ghost_model'" in e for e in errors)
