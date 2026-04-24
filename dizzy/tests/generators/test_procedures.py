"""Snapshot tests for procedures generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.procedures import (
    render_procedure_context,
    render_procedure_protocol,
    render_src_procedure_stub,
)
from tests.conftest import by_name


def test_render_procedure_context_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_procedure_context(by_name(recipe_feat.procedures, "extract_and_transform_recipe")) == snapshot


def test_render_procedure_protocol_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_procedure_protocol(by_name(recipe_feat.procedures, "extract_and_transform_recipe")) == snapshot


def test_render_src_procedure_stub_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_src_procedure_stub(by_name(recipe_feat.procedures, "extract_and_transform_recipe")) == snapshot
