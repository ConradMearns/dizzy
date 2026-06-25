"""Snapshot tests for events generator."""

from dizzy.generators.events import render_scaffold_events
from syrupy.assertion import SnapshotAssertion


def test_render_scaffold_events_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_events(recipe_feat.events) == snapshot
