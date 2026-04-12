"""Snapshot tests for models generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.models import render_scaffold_model


def test_render_scaffold_model_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_model("recipes", recipe_feat) == snapshot
