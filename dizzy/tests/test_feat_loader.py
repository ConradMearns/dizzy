"""Tests for feat_loader — YAML loading, normalization, and validation."""

from pathlib import Path

import pytest

from dizzy.feat_loader import FeatureDefinition, load_feat, validate_feat
from dizzy.feat_schema import (
    CommandDef,
    EventDef,
    ModelDef,
    PolicyDef,
    ProcedureDef,
    ProjectionDef,
    QueryDef,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestLoadFeat:
    def test_loads_recipe(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        assert feat.description == "Recipe App"

    def test_recipe_models(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        assert "recipes" in feat.models
        assert feat.models["recipes"].adapters == ["sqla", "relative_filesystem"]

    def test_recipe_queries(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        assert "get_recipe_text" in feat.queries
        q = feat.queries["get_recipe_text"]
        assert q.model == "recipes"
        assert q.adapter == "relative_filesystem"

    def test_recipe_query_different_adapter(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        q = feat.queries["get_recipe"]
        assert q.model == "recipes"
        assert q.adapter == "sqla"

    def test_command_string_shorthand(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        cmd = feat.commands["ingest_recipe_text"]
        assert isinstance(cmd, CommandDef)
        assert cmd.description == "Initiates ingestion of a recipe from a raw text source"

    def test_event_string_shorthand(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        evt = feat.events["recipe_ingested"]
        assert isinstance(evt, EventDef)

    def test_procedure(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        proc = feat.procedures["extract_and_transform_recipe"]
        assert proc.command == "ingest_recipe_text"
        assert "get_recipe_text" in proc.queries
        assert "recipe_ingested" in proc.emits

    def test_policy(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        policy = feat.policies["index_recipe_on_ingest"]
        assert policy.event == "recipe_ingested"

    def test_projection_with_adapter(self):
        feat = load_feat(FIXTURES_DIR / "recipe.feat.yaml")
        proj = feat.projections["recipe_library"]
        assert proj.event == "recipe_ingested"
        assert proj.model == "recipes"
        assert proj.adapter == "sqla"

    def test_loads_partial(self):
        feat = load_feat(FIXTURES_DIR / "partial.feat.yaml")
        assert "do_thing" in feat.commands
        assert "find_thing" in feat.queries
        assert "run_thing" in feat.procedures
        assert not feat.models
        assert not feat.events
        assert not feat.policies
        assert not feat.projections

    def test_partial_query_no_model(self):
        feat = load_feat(FIXTURES_DIR / "partial.feat.yaml")
        q = feat.queries["find_thing"]
        assert q.model is None
        assert q.adapter is None


class TestValidateFeat:
    def test_valid_recipe(self, recipe_feat):
        assert validate_feat(recipe_feat) == []

    def test_valid_partial(self, partial_feat):
        assert validate_feat(partial_feat) == []

    def test_procedure_unknown_command(self):
        feat = FeatureDefinition(
            commands={"do_thing": CommandDef(name="do_thing", description="does a thing")},
            procedures={
                "my_proc": ProcedureDef(
                    name="my_proc", description="proc", command="unknown_command"
                )
            },
        )
        errors = validate_feat(feat)
        assert any("command 'unknown_command'" in e for e in errors)

    def test_procedure_unknown_query(self):
        feat = FeatureDefinition(
            commands={"do_thing": CommandDef(name="do_thing", description="does a thing")},
            queries={"real_query": QueryDef(name="real_query", description="real")},
            procedures={
                "my_proc": ProcedureDef(
                    name="my_proc",
                    description="proc",
                    command="do_thing",
                    queries=["missing_query"],
                )
            },
        )
        errors = validate_feat(feat)
        assert any("query 'missing_query'" in e for e in errors)

    def test_procedure_emits_unknown_event(self):
        feat = FeatureDefinition(
            commands={"do_thing": CommandDef(name="do_thing", description="does a thing")},
            events={"real_event": EventDef(name="real_event", description="real")},
            procedures={
                "my_proc": ProcedureDef(
                    name="my_proc",
                    description="proc",
                    command="do_thing",
                    emits=["ghost_event"],
                )
            },
        )
        errors = validate_feat(feat)
        assert any("emits 'ghost_event'" in e for e in errors)

    def test_policy_unknown_event(self):
        feat = FeatureDefinition(
            events={"real_event": EventDef(name="real_event", description="real")},
            policies={
                "my_policy": PolicyDef(
                    name="my_policy", description="policy", event="unknown_event"
                )
            },
        )
        errors = validate_feat(feat)
        assert any("event 'unknown_event'" in e for e in errors)

    def test_policy_emits_unknown_command(self):
        feat = FeatureDefinition(
            commands={"real_cmd": CommandDef(name="real_cmd", description="real")},
            events={"some_event": EventDef(name="some_event", description="event")},
            policies={
                "my_policy": PolicyDef(
                    name="my_policy",
                    description="policy",
                    event="some_event",
                    emits=["ghost_cmd"],
                )
            },
        )
        errors = validate_feat(feat)
        assert any("emits 'ghost_cmd'" in e for e in errors)

    def test_projection_unknown_event(self):
        feat = FeatureDefinition(
            events={"real_event": EventDef(name="real_event", description="real")},
            projections={
                "my_proj": ProjectionDef(
                    name="my_proj", description="proj", event="unknown_event"
                )
            },
        )
        errors = validate_feat(feat)
        assert any("event 'unknown_event'" in e for e in errors)

    def test_projection_unknown_model(self):
        feat = FeatureDefinition(
            models={
                "real_model": ModelDef(
                    name="real_model", description="a real model", adapters=["sqla"]
                )
            },
            events={"some_event": EventDef(name="some_event", description="event")},
            projections={
                "my_proj": ProjectionDef(
                    name="my_proj",
                    description="proj",
                    event="some_event",
                    model="ghost_model",
                    adapter="sqla",
                )
            },
        )
        errors = validate_feat(feat)
        assert any("model 'ghost_model'" in e for e in errors)

    def test_query_unknown_model(self):
        feat = FeatureDefinition(
            models={
                "real_model": ModelDef(
                    name="real_model", description="a real model", adapters=["sqla"]
                )
            },
            queries={
                "my_query": QueryDef(
                    name="my_query",
                    description="query",
                    model="ghost_model",
                    adapter="sqla",
                )
            },
        )
        errors = validate_feat(feat)
        assert any("model 'ghost_model'" in e for e in errors)

    def test_query_model_without_adapter(self):
        feat = FeatureDefinition(
            models={
                "recipes": ModelDef(
                    name="recipes", description="recipes", adapters=["sqla"]
                )
            },
            queries={
                "my_query": QueryDef(
                    name="my_query", description="query", model="recipes"
                )
            },
        )
        errors = validate_feat(feat)
        assert any("model declared without adapter" in e for e in errors)

    def test_query_adapter_without_model(self):
        feat = FeatureDefinition(
            queries={
                "my_query": QueryDef(
                    name="my_query", description="query", adapter="sqla"
                )
            },
        )
        errors = validate_feat(feat)
        assert any("adapter declared without model" in e for e in errors)

    def test_query_adapter_not_in_model(self):
        feat = FeatureDefinition(
            models={
                "recipes": ModelDef(
                    name="recipes", description="recipes", adapters=["sqla"]
                )
            },
            queries={
                "my_query": QueryDef(
                    name="my_query",
                    description="query",
                    model="recipes",
                    adapter="relative_filesystem",
                )
            },
        )
        errors = validate_feat(feat)
        assert any(
            "adapter 'relative_filesystem' not declared on model 'recipes'" in e
            for e in errors
        )

    def test_projection_model_without_adapter(self):
        feat = FeatureDefinition(
            models={
                "recipes": ModelDef(
                    name="recipes", description="recipes", adapters=["sqla"]
                )
            },
            events={"some_event": EventDef(name="some_event", description="event")},
            projections={
                "my_proj": ProjectionDef(
                    name="my_proj",
                    description="proj",
                    event="some_event",
                    model="recipes",
                )
            },
        )
        errors = validate_feat(feat)
        assert any("model declared without adapter" in e for e in errors)

    def test_projection_adapter_without_model(self):
        feat = FeatureDefinition(
            events={"some_event": EventDef(name="some_event", description="event")},
            projections={
                "my_proj": ProjectionDef(
                    name="my_proj",
                    description="proj",
                    event="some_event",
                    adapter="sqla",
                )
            },
        )
        errors = validate_feat(feat)
        assert any("adapter declared without model" in e for e in errors)

    def test_projection_adapter_not_in_model(self):
        feat = FeatureDefinition(
            models={
                "recipes": ModelDef(
                    name="recipes", description="recipes", adapters=["sqla"]
                )
            },
            events={"some_event": EventDef(name="some_event", description="event")},
            projections={
                "my_proj": ProjectionDef(
                    name="my_proj",
                    description="proj",
                    event="some_event",
                    model="recipes",
                    adapter="relative_filesystem",
                )
            },
        )
        errors = validate_feat(feat)
        assert any(
            "adapter 'relative_filesystem' not declared on model 'recipes'" in e
            for e in errors
        )
