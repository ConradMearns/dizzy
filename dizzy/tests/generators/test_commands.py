"""Tests for commands generator."""

from pathlib import Path
from typing import Any

from dizzy.feat import AttributeDef, CommandDef, FeatureDefinition
from dizzy.generators.commands import render_scaffold_commands


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



def test_render_scaffold_commands_write_skips_if_exists(tmp_path: Path, recipe_feat: FeatureDefinition) -> None:
    from dizzy.generators.commands import write_scaffold_commands

    dest = tmp_path / "def" / "commands.yaml"
    dest.parent.mkdir(parents=True)
    dest.write_text("existing content")
    write_scaffold_commands(recipe_feat, tmp_path)
    assert dest.read_text() == "existing content"


def test_render_scaffold_commands_write_creates_file(tmp_path: Path, recipe_feat: FeatureDefinition) -> None:
    from dizzy.generators.commands import write_scaffold_commands

    write_scaffold_commands(recipe_feat, tmp_path)
    dest = tmp_path / "def" / "commands.yaml"
    assert dest.exists()
    assert "ingest_recipe_text" in dest.read_text()



def test_render_scaffold_commands_plain_string() -> None:
    """A command declared as a plain string parses and renders with empty attributes."""
    from dizzy.feat import _parse_command_def

    cmd = _parse_command_def("Does the thing")
    assert cmd.description == "Does the thing"
    assert cmd.attributes == {}

    feat = FeatureDefinition(commands={"do_thing": cmd})
    result = render_scaffold_commands(feat)
    assert "do_thing:" in result
    assert "Does the thing" in result
    assert "attributes: {}" in result


def test_render_scaffold_commands_empty_section() -> None:
    """An empty commands section renders only the LinkML header with no class entries."""
    feat = FeatureDefinition()
    result = render_scaffold_commands(feat)
    assert "id: https://example.org/commands" in result
    assert "classes:" in result
    # no command names in output
    lines = result.splitlines()
    class_idx = next(i for i, l in enumerate(lines) if l.strip() == "classes:")
    assert all(not l.strip() for l in lines[class_idx + 1 :])


def test_render_scaffold_commands_snapshot(recipe_feat: FeatureDefinition, snapshot: Any) -> None:
    result = render_scaffold_commands(recipe_feat)
    assert result == snapshot


