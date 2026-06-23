"""Snapshot tests for telemetry generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.telemetry import render_scaffold_telemetry


def test_render_scaffold_telemetry_snapshot(agent_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_telemetry(agent_feat.telemetry) == snapshot
