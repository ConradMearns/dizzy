"""Snapshot tests for projections generator."""

from dizzy.generators.projections import render_projection, render_src_projection_stub
from syrupy.assertion import SnapshotAssertion

from tests.conftest import by_name


def test_render_projection_with_adapter(recipe_feat, snapshot: SnapshotAssertion):
    assert render_projection(by_name(recipe_feat.projections, "recipe_library")) == snapshot


def test_render_src_projection_stub_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert (
        render_src_projection_stub(by_name(recipe_feat.projections, "recipe_library")) == snapshot
    )


def test_render_projection_with_env_telemetry_snapshot(agent_feat, snapshot: SnapshotAssertion):
    assert render_projection(by_name(agent_feat.projections, "conversation_log")) == snapshot
