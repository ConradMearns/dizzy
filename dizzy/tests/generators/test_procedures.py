"""Tests for procedures generator."""

from pathlib import Path
from typing import Any

from dizzy.feat import CommandDef, EventDef, FeatureDefinition, ProcedureDef, QueryDef
from dizzy.generators.procedures import (
    render_procedure_context,
    render_procedure_protocol,
)


# ---------------------------------------------------------------------------
# render_procedure_context
# ---------------------------------------------------------------------------


def test_render_procedure_context_auto_generated(recipe_feat: FeatureDefinition) -> None:
    result = render_procedure_context("extract_and_transform_recipe", recipe_feat)
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_procedure_context_imports(recipe_feat: FeatureDefinition) -> None:
    result = render_procedure_context("extract_and_transform_recipe", recipe_feat)
    assert "from dataclasses import dataclass" in result
    assert "from typing import Callable" in result
    assert "from gen_def.pydantic.events import recipe_ingested" in result
    assert (
        "from gen_int.python.query.get_recipe_text import get_recipe_text_query"
        in result
    )


def test_render_procedure_context_emitters_dataclass(
    recipe_feat: FeatureDefinition,
) -> None:
    result = render_procedure_context("extract_and_transform_recipe", recipe_feat)
    assert "@dataclass" in result
    assert "class extract_and_transform_recipe_emitters:" in result
    assert "recipe_ingested: Callable[[recipe_ingested], None]" in result


def test_render_procedure_context_queries_dataclass(
    recipe_feat: FeatureDefinition,
) -> None:
    result = render_procedure_context("extract_and_transform_recipe", recipe_feat)
    assert "class extract_and_transform_recipe_queries:" in result
    assert "get_recipe_text: get_recipe_text_query" in result


def test_render_procedure_context_context_dataclass(
    recipe_feat: FeatureDefinition,
) -> None:
    result = render_procedure_context("extract_and_transform_recipe", recipe_feat)
    assert "class extract_and_transform_recipe_context:" in result
    assert "emit: extract_and_transform_recipe_emitters" in result
    assert "query: extract_and_transform_recipe_queries" in result


def test_render_procedure_context_no_queries() -> None:
    feat = FeatureDefinition(
        commands={"do_thing": CommandDef(description="Do a thing")},
        events={"thing_done": EventDef(description="Thing was done")},
        procedures={
            "handle_thing": ProcedureDef(
                description="Handles the thing",
                command="do_thing",
                queries=[],
                emits=["thing_done"],
            )
        },
    )
    result = render_procedure_context("handle_thing", feat)
    assert "class handle_thing_emitters:" in result
    assert "thing_done: Callable[[thing_done], None]" in result
    # no queries dataclass and no query field in context
    assert "handle_thing_queries" not in result
    assert "query:" not in result
    assert "class handle_thing_context:" in result
    assert "emit: handle_thing_emitters" in result


def test_render_procedure_context_no_emits() -> None:
    feat = FeatureDefinition(
        commands={"read_data": CommandDef(description="Read some data")},
        queries={"get_item": QueryDef(description="Get an item", model="mydb")},
        procedures={
            "process": ProcedureDef(
                description="Processes data",
                command="read_data",
                queries=["get_item"],
                emits=[],
            )
        },
    )
    result = render_procedure_context("process", feat)
    assert "from typing import Callable" not in result
    assert "class process_emitters:" in result
    assert "pass" in result
    assert "class process_queries:" in result
    assert "get_item: get_item_query" in result
    assert "emit: process_emitters" in result
    assert "query: process_queries" in result


# ---------------------------------------------------------------------------
# render_procedure_protocol
# ---------------------------------------------------------------------------


def test_render_procedure_protocol_auto_generated(recipe_feat: FeatureDefinition) -> None:
    result = render_procedure_protocol("extract_and_transform_recipe", recipe_feat)
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_procedure_protocol_imports(recipe_feat: FeatureDefinition) -> None:
    result = render_procedure_protocol("extract_and_transform_recipe", recipe_feat)
    assert "from typing import Protocol" in result
    assert "from gen_def.pydantic.commands import ingest_recipe_text" in result
    assert (
        "from gen_int.python.procedure.extract_and_transform_recipe_context import ("
        in result
    )
    assert "    extract_and_transform_recipe_context," in result


def test_render_procedure_protocol_class(recipe_feat: FeatureDefinition) -> None:
    result = render_procedure_protocol("extract_and_transform_recipe", recipe_feat)
    assert "class extract_and_transform_recipe_protocol(Protocol):" in result


def test_render_procedure_protocol_docstring(recipe_feat: FeatureDefinition) -> None:
    result = render_procedure_protocol("extract_and_transform_recipe", recipe_feat)
    assert "Queries raw recipe text via source_ref" in result


def test_render_procedure_protocol_call_signature(recipe_feat: FeatureDefinition) -> None:
    result = render_procedure_protocol("extract_and_transform_recipe", recipe_feat)
    assert "def __call__(" in result
    assert "context: extract_and_transform_recipe_context," in result
    assert "command: ingest_recipe_text," in result
    assert ") -> None:" in result
    assert "..." in result


# ---------------------------------------------------------------------------
# writer tests
# ---------------------------------------------------------------------------


def test_write_procedure_context_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.procedures import write_procedure_context

    write_procedure_context("extract_and_transform_recipe", recipe_feat, tmp_path)
    dest = (
        tmp_path
        / "gen_int"
        / "python"
        / "procedure"
        / "extract_and_transform_recipe_context.py"
    )
    assert dest.exists()
    assert "class extract_and_transform_recipe_context" in dest.read_text()


def test_write_procedure_protocol_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.procedures import write_procedure_protocol

    write_procedure_protocol("extract_and_transform_recipe", recipe_feat, tmp_path)
    dest = (
        tmp_path
        / "gen_int"
        / "python"
        / "procedure"
        / "extract_and_transform_recipe_protocol.py"
    )
    assert dest.exists()
    assert "class extract_and_transform_recipe_protocol" in dest.read_text()


def test_write_procedure_src_stub_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.procedures import write_procedure_src_stub

    write_procedure_src_stub("extract_and_transform_recipe", recipe_feat, tmp_path)
    dest = tmp_path / "src" / "procedure" / "extract_and_transform_recipe.py"
    assert dest.exists()
    assert "raise NotImplementedError" in dest.read_text()


def test_write_procedure_src_stub_skips_if_exists(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.procedures import write_procedure_src_stub

    dest = tmp_path / "src" / "procedure" / "extract_and_transform_recipe.py"
    dest.parent.mkdir(parents=True)
    dest.write_text("my implementation")
    write_procedure_src_stub("extract_and_transform_recipe", recipe_feat, tmp_path)
    assert dest.read_text() == "my implementation"


# ---------------------------------------------------------------------------
# snapshot tests
# ---------------------------------------------------------------------------


def test_render_procedure_context_snapshot(
    recipe_feat: FeatureDefinition, snapshot: Any
) -> None:
    result = render_procedure_context("extract_and_transform_recipe", recipe_feat)
    assert result == snapshot


def test_render_procedure_protocol_snapshot(
    recipe_feat: FeatureDefinition, snapshot: Any
) -> None:
    result = render_procedure_protocol("extract_and_transform_recipe", recipe_feat)
    assert result == snapshot
