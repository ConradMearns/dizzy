"""Tests for commands generator."""

import pytest

from dizzy.feat import AttributeDef, CommandDef, FeatureDefinition
from dizzy.generators.commands import render_gen_commands, render_scaffold_commands


def test_render_scaffold_commands_basic(recipe_feat):
    result = render_scaffold_commands(recipe_feat)
    assert "classes:" in result
    assert "ingest_recipe_text:" in result
    assert "Initiates ingestion of a recipe from a raw text source" in result


def test_render_scaffold_commands_linkml_header(recipe_feat):
    result = render_scaffold_commands(recipe_feat)
    assert "id: https://example.org/commands" in result
    assert "name: commands" in result
    assert "imports:" in result
    assert "linkml:types" in result


def test_render_scaffold_commands_no_attributes(recipe_feat):
    result = render_scaffold_commands(recipe_feat)
    # ingest_recipe_text has no attributes — should emit empty attributes map
    assert "attributes: {}" in result


def test_render_scaffold_commands_with_attributes():
    feat = FeatureDefinition(
        commands={
            "upload_blob": CommandDef(
                description="Uploads a blob",
                attributes={
                    "manifest_id": AttributeDef(type="string", required=True),
                    "notes": AttributeDef(type="string", required=False),
                },
            )
        }
    )
    result = render_scaffold_commands(feat)
    assert "upload_blob:" in result
    assert "manifest_id:" in result
    assert "range: string" in result
    assert "required: true" in result
    assert "notes:" in result
    # notes is not required — no required: true line for it
    lines = result.splitlines()
    notes_idx = next(i for i, l in enumerate(lines) if "notes:" in l)
    # the lines after notes should not have required: true before next attribute
    notes_block = lines[notes_idx : notes_idx + 5]
    assert not any("required: true" in l for l in notes_block)


def test_render_gen_commands_basic(recipe_feat):
    result = render_gen_commands(recipe_feat)
    assert "# AUTO-GENERATED" in result
    assert "from pydantic import BaseModel" in result
    assert "class ingest_recipe_text(BaseModel):" in result
    assert "Initiates ingestion of a recipe from a raw text source" in result
    assert "pass" in result  # no attributes → pass body


def test_render_gen_commands_with_required_attribute():
    feat = FeatureDefinition(
        commands={
            "create_item": CommandDef(
                description="Creates an item",
                attributes={
                    "item_id": AttributeDef(type="string", required=True),
                },
            )
        }
    )
    result = render_gen_commands(feat)
    assert "class create_item(BaseModel):" in result
    assert "item_id: str" in result
    assert "Optional" not in result


def test_render_gen_commands_with_optional_attribute():
    feat = FeatureDefinition(
        commands={
            "create_item": CommandDef(
                description="Creates an item",
                attributes={
                    "notes": AttributeDef(type="string", required=False),
                },
            )
        }
    )
    result = render_gen_commands(feat)
    assert "from typing import Optional" in result
    assert "notes: Optional[str] = None" in result


def test_render_scaffold_commands_write_skips_if_exists(tmp_path, recipe_feat):
    from dizzy.generators.commands import write_scaffold_commands

    dest = tmp_path / "def" / "commands.yaml"
    dest.parent.mkdir(parents=True)
    dest.write_text("existing content")
    write_scaffold_commands(recipe_feat, tmp_path)
    assert dest.read_text() == "existing content"


def test_render_scaffold_commands_write_creates_file(tmp_path, recipe_feat):
    from dizzy.generators.commands import write_scaffold_commands

    write_scaffold_commands(recipe_feat, tmp_path)
    dest = tmp_path / "def" / "commands.yaml"
    assert dest.exists()
    assert "ingest_recipe_text" in dest.read_text()


def test_write_gen_commands_creates_file(tmp_path, recipe_feat):
    from dizzy.generators.commands import write_gen_commands

    write_gen_commands(recipe_feat, tmp_path)
    dest = tmp_path / "gen_def" / "pydantic" / "commands.py"
    assert dest.exists()
    assert "class ingest_recipe_text" in dest.read_text()
