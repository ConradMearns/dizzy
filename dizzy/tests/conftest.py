"""Shared fixtures for dizzy tests."""

from pathlib import Path

import pytest
from dizzy.feat_loader import load_feat
from dizzy.feat_schema import FeatureDefinition

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def by_name(items: list, name: str):
    """Find a Def object in a list by its name field."""
    return next(item for item in items if item.name == name)


@pytest.fixture
def recipe_feat() -> FeatureDefinition:
    """Full recipe example feat — used across all generator tests."""
    return load_feat(FIXTURES_DIR / "recipe.feat.yaml")


@pytest.fixture
def partial_feat() -> FeatureDefinition:
    """Partial feat — commands, queries, procedures only (no models/events/policies/projections)."""
    return load_feat(FIXTURES_DIR / "partial.feat.yaml")


@pytest.fixture
def agent_feat() -> FeatureDefinition:
    """Agent feat — exercises environment + telemetry across all four function kinds."""
    return load_feat(FIXTURES_DIR / "agent.feat.yaml")
