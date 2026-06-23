"""Snapshot tests for environment generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.environment import render_scaffold_environment


def test_render_scaffold_environment_snapshot(agent_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_environment(agent_feat.environment) == snapshot
