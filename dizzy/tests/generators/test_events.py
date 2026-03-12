"""Tests for events generator."""

from pathlib import Path
from typing import Any

from dizzy.feat import AttributeDef, EventDef, FeatureDefinition
from dizzy.generators.events import render_scaffold_events


def test_render_scaffold_events_basic(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_events(recipe_feat)
    assert "classes:" in result
    assert "recipe_ingested:" in result
    assert "A recipe was successfully extracted and validated" in result


def test_render_scaffold_events_linkml_header(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_events(recipe_feat)
    assert "id: https://example.org/events" in result
    assert "name: events" in result
    assert "imports:" in result
    assert "linkml:types" in result


def test_render_scaffold_events_with_attributes(recipe_feat: FeatureDefinition) -> None:
    result = render_scaffold_events(recipe_feat)
    # recipe_ingested has recipe_id and source_ref attributes
    assert "recipe_id:" in result
    assert "source_ref:" in result
    assert "range: string" in result
    assert "required: true" in result


def test_render_scaffold_events_no_attributes() -> None:
    feat = FeatureDefinition(
        events={"something_happened": EventDef(description="Something happened")}
    )
    result = render_scaffold_events(feat)
    assert "attributes: {}" in result


def test_render_scaffold_events_optional_attribute() -> None:
    feat = FeatureDefinition(
        events={
            "scan_item_found": EventDef(
                description="Found a file while scanning",
                attributes={
                    "file_path": AttributeDef(type="string", required=True),
                    "file_hash": AttributeDef(type="string", required=False),
                },
            )
        }
    )
    result = render_scaffold_events(feat)
    assert "file_path:" in result
    assert "file_hash:" in result
    lines = result.splitlines()
    hash_idx = next(i for i, l in enumerate(lines) if "file_hash:" in l)
    hash_block = lines[hash_idx : hash_idx + 5]
    assert not any("required: true" in l for l in hash_block)



def test_write_scaffold_events_skips_if_exists(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.events import write_scaffold_events

    dest = tmp_path / "def" / "events.yaml"
    dest.parent.mkdir(parents=True)
    dest.write_text("existing content")
    write_scaffold_events(recipe_feat, tmp_path)
    assert dest.read_text() == "existing content"


def test_write_scaffold_events_creates_file(
    tmp_path: Path, recipe_feat: FeatureDefinition
) -> None:
    from dizzy.generators.events import write_scaffold_events

    write_scaffold_events(recipe_feat, tmp_path)
    dest = tmp_path / "def" / "events.yaml"
    assert dest.exists()
    assert "recipe_ingested" in dest.read_text()



def test_render_scaffold_events_snapshot(
    recipe_feat: FeatureDefinition, snapshot: Any
) -> None:
    result = render_scaffold_events(recipe_feat)
    assert result == snapshot


