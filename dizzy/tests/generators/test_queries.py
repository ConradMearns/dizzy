"""Snapshot tests for queries generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.queries import render_scaffold_query, render_gen_query_protocol, render_src_query_stub


def test_render_scaffold_query_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_query("get_recipe_text", recipe_feat) == snapshot


def test_render_gen_query_protocol_with_adapter(recipe_feat, snapshot: SnapshotAssertion):
    assert render_gen_query_protocol("get_recipe_text", recipe_feat) == snapshot


def test_render_gen_query_protocol_no_adapter(partial_feat, snapshot: SnapshotAssertion):
    assert render_gen_query_protocol("find_thing", partial_feat) == snapshot


def test_render_src_query_stub(snapshot: SnapshotAssertion):
    assert render_src_query_stub("get_recipe_text") == snapshot
