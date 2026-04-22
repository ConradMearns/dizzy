"""Snapshot tests for models generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.models import render_scaffold_model
from tests.conftest import by_name


def test_render_scaffold_model_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_model(by_name(recipe_feat.models, "recipes")) == snapshot
