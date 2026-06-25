"""Snapshot tests for policies generator."""

from dizzy.generators.policies import (
    render_policy_context,
    render_policy_protocol,
    render_src_policy_stub,
)
from syrupy.assertion import SnapshotAssertion

from tests.conftest import by_name


def test_render_policy_context_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert (
        render_policy_context(by_name(recipe_feat.policies, "index_recipe_on_ingest")) == snapshot
    )


def test_render_policy_protocol_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert (
        render_policy_protocol(by_name(recipe_feat.policies, "index_recipe_on_ingest")) == snapshot
    )


def test_render_src_policy_stub_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert (
        render_src_policy_stub(by_name(recipe_feat.policies, "index_recipe_on_ingest")) == snapshot
    )


def test_render_policy_context_with_env_telemetry_snapshot(agent_feat, snapshot: SnapshotAssertion):
    assert render_policy_context(by_name(agent_feat.policies, "notify_on_reply")) == snapshot
