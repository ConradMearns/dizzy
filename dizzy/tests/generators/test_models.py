"""Tests for models generator."""

from pathlib import Path
from typing import Any

from dizzy.feat import FeatureDefinition
from dizzy.generators.models import (
    render_gen_model_pydantic,
    render_gen_model_sqla,
    render_scaffold_model,
)

_SIMPLE_DEF = """\
classes:
  Recipe:
    attributes:
      title:
        range: string
        required: true
      notes:
        range: string
  Step:
    attributes:
      body:
        range: string
        required: true
"""


def _make_def_dir(tmp_path: Path, schema_name: str, content: str) -> Path:
    def_file = tmp_path / "def" / "models" / f"{schema_name}.yaml"
    def_file.parent.mkdir(parents=True)
    def_file.write_text(content)
    return tmp_path


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
# render_gen_model_pydantic
# ---------------------------------------------------------------------------


def test_render_gen_model_pydantic_auto_generated(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_pydantic("recipes", def_dir)
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_gen_model_pydantic_imports(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_pydantic("recipes", def_dir)
    assert "from pydantic import BaseModel" in result


def test_render_gen_model_pydantic_classes(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_pydantic("recipes", def_dir)
    assert "class Recipe(BaseModel):" in result
    assert "class Step(BaseModel):" in result


def test_render_gen_model_pydantic_required_field(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_pydantic("recipes", def_dir)
    assert "title: str" in result
    assert "body: str" in result


def test_render_gen_model_pydantic_optional_field(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_pydantic("recipes", def_dir)
    assert "from typing import Optional" in result
    assert "notes: Optional[str] = None" in result


def test_render_gen_model_pydantic_no_optional_when_all_required(tmp_path: Path) -> None:
    content = """\
classes:
  Item:
    attributes:
      name:
        range: string
        required: true
"""
    def_dir = _make_def_dir(tmp_path, "items", content)
    result = render_gen_model_pydantic("items", def_dir)
    assert "Optional" not in result


def test_render_gen_model_pydantic_integer_type(tmp_path: Path) -> None:
    content = """\
classes:
  Step:
    attributes:
      order:
        range: integer
        required: true
"""
    def_dir = _make_def_dir(tmp_path, "steps", content)
    result = render_gen_model_pydantic("steps", def_dir)
    assert "order: int" in result


def test_render_gen_model_pydantic_empty_class(tmp_path: Path) -> None:
    content = "classes:\n  Empty:\n"
    def_dir = _make_def_dir(tmp_path, "empty", content)
    result = render_gen_model_pydantic("empty", def_dir)
    assert "class Empty(BaseModel):" in result
    assert "pass" in result


# ---------------------------------------------------------------------------
# render_gen_model_sqla
# ---------------------------------------------------------------------------


def test_render_gen_model_sqla_auto_generated(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_sqla("recipes", def_dir)
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_gen_model_sqla_imports(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_sqla("recipes", def_dir)
    assert "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column" in result
    assert "from sqlalchemy import" in result


def test_render_gen_model_sqla_base_class(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_sqla("recipes", def_dir)
    assert "class Base(DeclarativeBase):" in result


def test_render_gen_model_sqla_classes(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_sqla("recipes", def_dir)
    assert "class Recipe(Base):" in result
    assert "class Step(Base):" in result


def test_render_gen_model_sqla_tablename(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_sqla("recipes", def_dir)
    assert '__tablename__ = "recipe"' in result
    assert '__tablename__ = "step"' in result


def test_render_gen_model_sqla_primary_key(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_sqla("recipes", def_dir)
    assert "id: Mapped[int] = mapped_column(primary_key=True)" in result


def test_render_gen_model_sqla_required_field(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_sqla("recipes", def_dir)
    assert "title: Mapped[str] = mapped_column(String)" in result
    assert "body: Mapped[str] = mapped_column(String)" in result


def test_render_gen_model_sqla_optional_field(tmp_path: Path) -> None:
    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    result = render_gen_model_sqla("recipes", def_dir)
    assert "from typing import Optional" in result
    assert "notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)" in result


def test_render_gen_model_sqla_integer_column(tmp_path: Path) -> None:
    content = """\
classes:
  Step:
    attributes:
      order:
        range: integer
        required: true
"""
    def_dir = _make_def_dir(tmp_path, "steps", content)
    result = render_gen_model_sqla("steps", def_dir)
    assert "order: Mapped[int] = mapped_column(Integer)" in result
    assert "Integer" in result


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


def test_write_gen_model_pydantic_creates_file(tmp_path: Path) -> None:
    from dizzy.generators.models import write_gen_model_pydantic

    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    write_gen_model_pydantic("recipes", def_dir, tmp_path)
    dest = tmp_path / "gen_def" / "pydantic" / "models" / "recipes.py"
    assert dest.exists()
    assert "class Recipe(BaseModel):" in dest.read_text()


def test_write_gen_model_sqla_creates_file(tmp_path: Path) -> None:
    from dizzy.generators.models import write_gen_model_sqla

    def_dir = _make_def_dir(tmp_path, "recipes", _SIMPLE_DEF)
    write_gen_model_sqla("recipes", def_dir, tmp_path)
    dest = tmp_path / "gen_def" / "sqla" / "models" / "recipes.py"
    assert dest.exists()
    assert "class Recipe(Base):" in dest.read_text()


# ---------------------------------------------------------------------------
# snapshot tests
# ---------------------------------------------------------------------------


def test_render_scaffold_model_snapshot(recipe_feat: FeatureDefinition, snapshot: Any) -> None:
    result = render_scaffold_model("recipes", recipe_feat)
    assert result == snapshot


def test_render_gen_model_pydantic_snapshot(recipe_def_dir: Path, snapshot: Any) -> None:
    result = render_gen_model_pydantic("recipes", recipe_def_dir)
    assert result == snapshot


def test_render_gen_model_sqla_snapshot(recipe_def_dir: Path, snapshot: Any) -> None:
    result = render_gen_model_sqla("recipes", recipe_def_dir)
    assert result == snapshot
