"""Snapshot tests for telemetry generator."""

from dizzy.generators.telemetry import render_scaffold_telemetry
from syrupy.assertion import SnapshotAssertion


def test_render_scaffold_telemetry_snapshot(agent_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_telemetry(agent_feat.telemetry) == snapshot
