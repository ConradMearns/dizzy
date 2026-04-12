"""Snapshot tests for policies generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.policies import (
    render_policy_context,
    render_policy_protocol,
    render_src_policy_stub,
)


def test_render_policy_context_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_policy_context("index_recipe_on_ingest", recipe_feat) == snapshot


def test_render_policy_protocol_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_policy_protocol("index_recipe_on_ingest", recipe_feat) == snapshot


def test_render_src_policy_stub_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_src_policy_stub("index_recipe_on_ingest", recipe_feat) == snapshot
