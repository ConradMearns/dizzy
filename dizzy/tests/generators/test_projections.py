"""Tests for projections generator."""

from pathlib import Path
from typing import Any

from dizzy.feat import EventDef, FeatureDefinition, ProjectionDef
from dizzy.generators.projections import render_projection


# ---------------------------------------------------------------------------
# render_projection — context dataclass
# ---------------------------------------------------------------------------


def test_render_projection_auto_generated(recipe_feat: FeatureDefinition) -> None:
    result = render_projection("recipe_library", recipe_feat)
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_projection_imports(recipe_feat: FeatureDefinition) -> None:
    result = render_projection("recipe_library", recipe_feat)
    assert "from dataclasses import dataclass" in result
    assert "from typing import Protocol, Any" in result


def test_render_projection_event_import(recipe_feat: FeatureDefinition) -> None:
    result = render_projection("recipe_library", recipe_feat)
    assert "from gen_def.pydantic.events import recipe_ingested" in result


def test_render_projection_context_dataclass(recipe_feat: FeatureDefinition) -> None:
    result = render_projection("recipe_library", recipe_feat)
    assert "@dataclass" in result
    assert "class recipe_library_context:" in result
    assert '"""SQLAlchemy sessions for schemas written by this projection."""' in result
    assert "recipes: Any  # SQLAlchemy session for the recipes schema" in result


def test_render_projection_protocol_class(recipe_feat: FeatureDefinition) -> None:
    result = render_projection("recipe_library", recipe_feat)
    assert "class recipe_library_projection(Protocol):" in result


def test_render_projection_docstring(recipe_feat: FeatureDefinition) -> None:
    result = render_projection("recipe_library", recipe_feat)
    assert "Adds ingested recipe to the recipe library" in result


def test_render_projection_call_signature(recipe_feat: FeatureDefinition) -> None:
    result = render_projection("recipe_library", recipe_feat)
    assert "def __call__(self, event: recipe_ingested, context: recipe_library_context) -> None:" in result
    assert '"""Apply the projection — mutate model state in response to the event."""' in result
    assert "..." in result


def test_render_projection_multiple_models() -> None:
    feat = FeatureDefinition(
        events={"order_placed": EventDef(description="An order was placed")},
        projections={
            "order_summary": ProjectionDef(
                description="Builds order summary read model",
                event="order_placed",
                models=["orders", "customers"],
            )
        },
    )
    result = render_projection("order_summary", feat)
    assert "orders: Any  # SQLAlchemy session for the orders schema" in result
    assert "customers: Any  # SQLAlchemy session for the customers schema" in result
    assert "class order_summary_context:" in result
    assert "class order_summary_projection(Protocol):" in result
    assert "event: order_placed" in result
    assert "context: order_summary_context" in result


# ---------------------------------------------------------------------------
# writer tests
# ---------------------------------------------------------------------------


def test_write_projection_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.projections import write_projection

    write_projection("recipe_library", recipe_feat, tmp_path)
    dest = (
        tmp_path
        / "gen_int"
        / "python"
        / "projection"
        / "recipe_library_projection.py"
    )
    assert dest.exists()
    assert "class recipe_library_projection" in dest.read_text()


def test_write_projection_src_stub_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.projections import write_projection_src_stub

    write_projection_src_stub("recipe_library", recipe_feat, tmp_path)
    dest = tmp_path / "src" / "projection" / "recipe_library.py"
    assert dest.exists()
    assert "raise NotImplementedError" in dest.read_text()


def test_write_projection_src_stub_skips_if_exists(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.projections import write_projection_src_stub

    dest = tmp_path / "src" / "projection" / "recipe_library.py"
    dest.parent.mkdir(parents=True)
    dest.write_text("my implementation")
    write_projection_src_stub("recipe_library", recipe_feat, tmp_path)
    assert dest.read_text() == "my implementation"


# ---------------------------------------------------------------------------
# snapshot tests
# ---------------------------------------------------------------------------


def test_render_projection_snapshot(
    recipe_feat: FeatureDefinition, snapshot: Any
) -> None:
    result = render_projection("recipe_library", recipe_feat)
    assert result == snapshot
