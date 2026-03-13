"""Tests for models generator."""

from pathlib import Path
from typing import Any

from dizzy.feat import FeatureDefinition
from dizzy.generators.models import render_scaffold_model


# ---------------------------------------------------------------------------
# render_scaffold_model
# ---------------------------------------------------------------------------


def test_render_scaffold_model_basic(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_model("recipes", recipe_feat)
    assert "name: recipes" in result
    assert "Full recipe database" in result


def test_render_scaffold_model_linkml_header(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_model("recipes", recipe_feat)
    assert "id: https://example.org/models/recipes" in result
    assert "imports:" in result
    assert "linkml:types" in result
    assert "classes: {}" in result


def test_render_scaffold_model_includes_description(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_model("recipes", recipe_feat)
    assert "recipes, steps, and ingredients" in result


# ---------------------------------------------------------------------------
# writer tests
# ---------------------------------------------------------------------------


def test_write_scaffold_model_creates_file(tmp_path: Path, recipe_feat: FeatureDefinition) -> None:
    from dizzy.generators.models import write_scaffold_model

    write_scaffold_model("recipes", recipe_feat, tmp_path)
    dest = tmp_path / "def" / "models" / "recipes.yaml"
    assert dest.exists()
    assert "name: recipes" in dest.read_text()


def test_write_scaffold_model_skips_if_exists(tmp_path: Path, recipe_feat: FeatureDefinition) -> None:
    from dizzy.generators.models import write_scaffold_model

    dest = tmp_path / "def" / "models" / "recipes.yaml"
    dest.parent.mkdir(parents=True)
    dest.write_text("existing content")
    write_scaffold_model("recipes", recipe_feat, tmp_path)
    assert dest.read_text() == "existing content"


# ---------------------------------------------------------------------------
# snapshot tests
# ---------------------------------------------------------------------------


def test_render_scaffold_model_snapshot(recipe_feat: FeatureDefinition, snapshot: Any) -> None:
    result = render_scaffold_model("recipes", recipe_feat)
    assert result == snapshot
