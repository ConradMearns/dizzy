"""Snapshot tests for procedures generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.procedures import (
    render_procedure_context,
    render_procedure_protocol,
    render_src_procedure_stub,
)


def test_render_procedure_context_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_procedure_context("extract_and_transform_recipe", recipe_feat) == snapshot


def test_render_procedure_protocol_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_procedure_protocol("extract_and_transform_recipe", recipe_feat) == snapshot


def test_render_src_procedure_stub_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_src_procedure_stub("extract_and_transform_recipe", recipe_feat) == snapshot
