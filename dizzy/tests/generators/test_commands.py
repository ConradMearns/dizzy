"""Snapshot tests for commands generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.commands import render_scaffold_commands


def test_render_scaffold_commands_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_commands(recipe_feat) == snapshot


def test_render_scaffold_commands_partial(partial_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_commands(partial_feat) == snapshot
