"""Shared fixtures for dizzy tests."""

from pathlib import Path

import pytest

from dizzy.feat import FeatureDefinition, load_feat

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def recipe_feat() -> FeatureDefinition:
    """Full recipe example feat — used across all generator tests."""
    return load_feat(FIXTURES_DIR / "recipe.feat.yaml")


@pytest.fixture
def partial_feat() -> FeatureDefinition:
    """Partial feat — commands, queries, procedures only (no models/events/policies/projections)."""
    return load_feat(FIXTURES_DIR / "partial.feat.yaml")


