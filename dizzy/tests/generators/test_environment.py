"""Snapshot tests for environment generator."""

from dizzy.generators.environment import render_scaffold_environment
from syrupy.assertion import SnapshotAssertion


def test_render_scaffold_environment_snapshot(agent_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_environment(agent_feat.environment) == snapshot
