"""Tests for queries generator."""

from pathlib import Path
from typing import Any

from dizzy.feat import FeatureDefinition
from dizzy.generators.queries import (
    render_gen_query_protocol,
    render_scaffold_query,
)



def test_render_scaffold_query_linkml_header(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_query("get_recipe_text", recipe_feat)
    assert "id: https://example.org/queries/get_recipe_text" in result
    assert "name: get_recipe_text" in result
    assert "imports:" in result
    assert "linkml:types" in result


def test_render_scaffold_query_description(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_query("get_recipe_text", recipe_feat)
    assert "description: Retrieves raw recipe text given a source reference" in result


def test_render_scaffold_query_both_classes(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_query("get_recipe_text", recipe_feat)
    assert "classes:" in result
    assert "GetRecipeTextInput:" in result
    assert "GetRecipeTextOutput:" in result
    assert "attributes: {}" in result


def test_render_scaffold_query_class_descriptions(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_query("get_recipe_text", recipe_feat)
    assert "description: Input for get_recipe_text" in result
    assert "description: Output for get_recipe_text" in result


def test_render_scaffold_query_second_query(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_query("get_recipe", recipe_feat)
    assert "GetRecipeInput:" in result
    assert "GetRecipeOutput:" in result


def test_render_gen_query_protocol_auto_generated(recipe_feat: FeatureDefinition) -> None:
    result = render_gen_query_protocol("get_recipe_text", recipe_feat)
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_gen_query_protocol_imports(recipe_feat: FeatureDefinition) -> None:
    result = render_gen_query_protocol("get_recipe_text", recipe_feat)
    assert "from dataclasses import dataclass" in result
    assert "from typing import Protocol, Any" in result
    assert "from gen_def.pydantic.query.get_recipe_text import GetRecipeTextInput, GetRecipeTextOutput" in result


def test_render_gen_query_protocol_context_class(recipe_feat: FeatureDefinition) -> None:
    result = render_gen_query_protocol("get_recipe_text", recipe_feat)
    assert "@dataclass" in result
    assert "class get_recipe_text_context:" in result
    assert "recipes: Any" in result
    assert "SQLAlchemy session for the recipes schema" in result


def test_render_gen_query_protocol_protocol_class(recipe_feat: FeatureDefinition) -> None:
    result = render_gen_query_protocol("get_recipe_text", recipe_feat)
    assert "class get_recipe_text_query(Protocol):" in result
    assert "Retrieves raw recipe text given a source reference" in result
    assert "def __call__(" in result
    assert "input: GetRecipeTextInput" in result
    assert "context: get_recipe_text_context" in result
    assert "-> GetRecipeTextOutput:" in result
    assert "..." in result


def test_render_gen_query_protocol_second_query(recipe_feat: FeatureDefinition) -> None:
    result = render_gen_query_protocol("get_recipe", recipe_feat)
    assert "class get_recipe_context:" in result
    assert "class get_recipe_query(Protocol):" in result
    assert "Retrieves a structured recipe by ID" in result
    assert "recipes: Any" in result


def test_write_scaffold_query_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.queries import write_scaffold_query

    write_scaffold_query("get_recipe_text", recipe_feat, tmp_path)
    dest = tmp_path / "def" / "queries" / "get_recipe_text.yaml"
    assert dest.exists()
    content = dest.read_text()
    assert "GetRecipeTextInput" in content
    assert "GetRecipeTextOutput" in content


def test_write_scaffold_query_skips_if_exists(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.queries import write_scaffold_query

    dest = tmp_path / "def" / "queries" / "get_recipe_text.yaml"
    dest.parent.mkdir(parents=True)
    dest.write_text("existing content")
    write_scaffold_query("get_recipe_text", recipe_feat, tmp_path)
    assert dest.read_text() == "existing content"


def test_write_gen_query_protocol_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.queries import write_gen_query_protocol

    write_gen_query_protocol("get_recipe_text", recipe_feat, tmp_path)
    dest = tmp_path / "gen_int" / "python" / "query" / "get_recipe_text.py"
    assert dest.exists()
    assert "class get_recipe_text_query" in dest.read_text()


def test_write_src_query_stub_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.queries import write_src_query_stub

    write_src_query_stub("get_recipe_text", tmp_path)
    dest = tmp_path / "src" / "query" / "get_recipe_text.py"
    assert dest.exists()
    assert "raise NotImplementedError" in dest.read_text()


def test_write_src_query_stub_skips_if_exists(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.queries import write_src_query_stub

    dest = tmp_path / "src" / "query" / "get_recipe_text.py"
    dest.parent.mkdir(parents=True)
    dest.write_text("my implementation")
    write_src_query_stub("get_recipe_text", tmp_path)
    assert dest.read_text() == "my implementation"


def test_render_gen_query_protocol_model_none_omits_session_field(
    partial_feat: FeatureDefinition,
) -> None:
    result = render_gen_query_protocol("find_thing", partial_feat)
    assert "pass" in result
    assert "SQLAlchemy session" not in result
    assert "class find_thing_context:" in result
    assert "class find_thing_query(Protocol):" in result


def test_render_scaffold_query_snapshot(
    recipe_feat: FeatureDefinition, snapshot: Any
) -> None:
    result = render_scaffold_query("get_recipe_text", recipe_feat)
    assert result == snapshot


def test_render_gen_query_protocol_snapshot(
    recipe_feat: FeatureDefinition, snapshot: Any
) -> None:
    result = render_gen_query_protocol("get_recipe_text", recipe_feat)
    assert result == snapshot
