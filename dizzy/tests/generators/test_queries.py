"""Snapshot tests for queries generator."""

from syrupy.assertion import SnapshotAssertion

from dizzy.generators.queries import render_scaffold_query, render_gen_query_protocol, render_src_query_stub
from tests.conftest import by_name


def test_render_scaffold_query_snapshot(recipe_feat, snapshot: SnapshotAssertion):
    assert render_scaffold_query(by_name(recipe_feat.queries, "get_recipe_text")) == snapshot


def test_render_gen_query_protocol_with_adapter(recipe_feat, snapshot: SnapshotAssertion):
    assert render_gen_query_protocol(by_name(recipe_feat.queries, "get_recipe_text")) == snapshot


def test_render_gen_query_protocol_no_adapter(partial_feat, snapshot: SnapshotAssertion):
    assert render_gen_query_protocol(by_name(partial_feat.queries, "find_thing")) == snapshot


def test_render_src_query_stub(snapshot: SnapshotAssertion):
    assert render_src_query_stub("get_recipe_text") == snapshot


def test_render_gen_query_protocol_with_env_telemetry(agent_feat, snapshot: SnapshotAssertion):
    assert render_gen_query_protocol(by_name(agent_feat.queries, "get_conversation")) == snapshot
