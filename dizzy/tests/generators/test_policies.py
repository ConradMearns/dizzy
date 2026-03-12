"""Tests for policies generator."""

from pathlib import Path
from typing import Any

from dizzy.feat import CommandDef, EventDef, FeatureDefinition, PolicyDef
from dizzy.generators.policies import render_policy_context, render_policy_protocol


# ---------------------------------------------------------------------------
# render_policy_context
# ---------------------------------------------------------------------------


def test_render_policy_context_auto_generated(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_context("index_recipe_on_ingest", recipe_feat)
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_policy_context_imports(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_context("index_recipe_on_ingest", recipe_feat)
    assert "from dataclasses import dataclass" in result


def test_render_policy_context_no_emits_has_pass(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_context("index_recipe_on_ingest", recipe_feat)
    assert "class index_recipe_on_ingest_emitters:" in result
    assert "pass" in result
    assert "from typing import Callable" not in result


def test_render_policy_context_context_dataclass(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_context("index_recipe_on_ingest", recipe_feat)
    assert "class index_recipe_on_ingest_context:" in result
    assert "emit: index_recipe_on_ingest_emitters" in result


def test_render_policy_context_with_emits() -> None:
    feat = FeatureDefinition(
        commands={"do_thing": CommandDef(description="Do a thing")},
        events={"scan_complete": EventDef(description="Scan completed")},
        policies={
            "trigger_on_scan": PolicyDef(
                description="Triggers do_thing when scan completes",
                event="scan_complete",
                emits=["do_thing"],
            )
        },
    )
    result = render_policy_context("trigger_on_scan", feat)
    assert "from typing import Callable" in result
    assert "from gen_def.pydantic.commands import do_thing" in result
    assert "class trigger_on_scan_emitters:" in result
    assert "do_thing: Callable[[do_thing], None]" in result
    assert "class trigger_on_scan_context:" in result
    assert "emit: trigger_on_scan_emitters" in result
    assert "pass" not in result


# ---------------------------------------------------------------------------
# render_policy_protocol
# ---------------------------------------------------------------------------


def test_render_policy_protocol_auto_generated(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_protocol("index_recipe_on_ingest", recipe_feat)
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_policy_protocol_imports(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_protocol("index_recipe_on_ingest", recipe_feat)
    assert "from typing import Protocol" in result
    assert "from gen_def.pydantic.events import recipe_ingested" in result
    assert (
        "from gen_int.python.policy.index_recipe_on_ingest_context import (" in result
    )
    assert "    index_recipe_on_ingest_context," in result


def test_render_policy_protocol_class(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_protocol("index_recipe_on_ingest", recipe_feat)
    assert "class index_recipe_on_ingest_protocol(Protocol):" in result


def test_render_policy_protocol_docstring(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_protocol("index_recipe_on_ingest", recipe_feat)
    assert "Adds recipe to the library projection when ingested" in result


def test_render_policy_protocol_call_signature(recipe_feat: FeatureDefinition) -> None:
    result = render_policy_protocol("index_recipe_on_ingest", recipe_feat)
    assert "def __call__(" in result
    assert "event: recipe_ingested," in result
    assert "context: index_recipe_on_ingest_context," in result
    assert ") -> None:" in result
    assert "..." in result


# ---------------------------------------------------------------------------
# writer tests
# ---------------------------------------------------------------------------


def test_write_policy_context_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.policies import write_policy_context

    write_policy_context("index_recipe_on_ingest", recipe_feat, tmp_path)
    dest = (
        tmp_path
        / "gen_int"
        / "python"
        / "policy"
        / "index_recipe_on_ingest_context.py"
    )
    assert dest.exists()
    assert "class index_recipe_on_ingest_context" in dest.read_text()


def test_write_policy_protocol_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.policies import write_policy_protocol

    write_policy_protocol("index_recipe_on_ingest", recipe_feat, tmp_path)
    dest = (
        tmp_path
        / "gen_int"
        / "python"
        / "policy"
        / "index_recipe_on_ingest_protocol.py"
    )
    assert dest.exists()
    assert "class index_recipe_on_ingest_protocol" in dest.read_text()


def test_write_policy_src_stub_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.policies import write_policy_src_stub

    write_policy_src_stub("index_recipe_on_ingest", recipe_feat, tmp_path)
    dest = tmp_path / "src" / "policy" / "index_recipe_on_ingest.py"
    assert dest.exists()
    assert "raise NotImplementedError" in dest.read_text()


def test_write_policy_src_stub_skips_if_exists(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.policies import write_policy_src_stub

    dest = tmp_path / "src" / "policy" / "index_recipe_on_ingest.py"
    dest.parent.mkdir(parents=True)
    dest.write_text("my implementation")
    write_policy_src_stub("index_recipe_on_ingest", recipe_feat, tmp_path)
    assert dest.read_text() == "my implementation"


# ---------------------------------------------------------------------------
# snapshot tests
# ---------------------------------------------------------------------------


def test_render_policy_context_snapshot(
    recipe_feat: FeatureDefinition, snapshot: Any
) -> None:
    result = render_policy_context("index_recipe_on_ingest", recipe_feat)
    assert result == snapshot


def test_render_policy_protocol_snapshot(
    recipe_feat: FeatureDefinition, snapshot: Any
) -> None:
    result = render_policy_protocol("index_recipe_on_ingest", recipe_feat)
    assert result == snapshot
