"""Snapshot tests for adapters generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.adapters import render_adapter


def test_render_sqla_adapter(snapshot: SnapshotAssertion):
    assert render_adapter("sqla") == snapshot


def test_render_relative_filesystem_adapter(snapshot: SnapshotAssertion):
    assert render_adapter("relative_filesystem") == snapshot


def test_render_unknown_adapter():
    assert render_adapter("unknown") == ""
