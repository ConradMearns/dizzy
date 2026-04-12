"""Snapshot tests for events generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.events import render_scaffold_events


def test_render_scaffold_events_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_events(recipe_feat) == snapshot
