"""Snapshot tests for projections generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.projections import render_projection, render_src_projection_stub


def test_render_projection_with_adapter(recipe_feat, snapshot: SnapshotAssertion):
    assert render_projection("recipe_library", recipe_feat) == snapshot


def test_render_src_projection_stub_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_src_projection_stub("recipe_library", recipe_feat) == snapshot
