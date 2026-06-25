"""Tests for the scaffold YAML emission helper and multi-line-description safety."""

import yaml
from dizzy.feat_schema import CommandDef, EnvironmentDef, EventDef, ModelDef, QueryDef, TelemetryDef
from dizzy.generators.commands import render_scaffold_commands
from dizzy.generators.environment import render_scaffold_environment
from dizzy.generators.events import render_scaffold_events
from dizzy.generators.models import render_scaffold_model
from dizzy.generators.queries import render_scaffold_query
from dizzy.generators.telemetry import render_scaffold_telemetry
from dizzy.generators.yaml_util import description_lines

MULTILINE = "First line of the description.\nSecond line with: a colon.\nThird line."


def test_single_line_description_stays_inline():
    assert description_lines("hello", "    ") == ["    description: hello"]


def test_multiline_description_uses_block_scalar():
    out = description_lines(MULTILINE, "  ")
    assert out[0] == "  description: |-"
    parsed = yaml.safe_load("root:\n" + "\n".join(out))
    assert parsed["root"]["description"] == MULTILINE


def test_scaffold_commands_multiline_is_valid_yaml():
    text = render_scaffold_commands([CommandDef(name="do_thing", description=MULTILINE)])
    parsed = yaml.safe_load(text)
    assert parsed["classes"]["do_thing"]["description"] == MULTILINE


def test_scaffold_events_multiline_is_valid_yaml():
    text = render_scaffold_events([EventDef(name="thing_done", description=MULTILINE)])
    parsed = yaml.safe_load(text)
    assert parsed["classes"]["thing_done"]["description"] == MULTILINE


def test_scaffold_model_multiline_is_valid_yaml():
    text = render_scaffold_model(ModelDef(name="things", description=MULTILINE))
    parsed = yaml.safe_load(text)
    assert parsed["description"] == MULTILINE


def test_scaffold_query_multiline_is_valid_yaml():
    text = render_scaffold_query(QueryDef(name="get_thing", description=MULTILINE))
    parsed = yaml.safe_load(text)
    assert parsed["description"] == MULTILINE


def test_scaffold_environment_multiline_is_valid_yaml():
    text = render_scaffold_environment([EnvironmentDef(name="model", description=MULTILINE)])
    parsed = yaml.safe_load(text)
    assert parsed["classes"]["model"]["description"] == MULTILINE


def test_scaffold_telemetry_multiline_is_valid_yaml():
    text = render_scaffold_telemetry([TelemetryDef(name="stream_chunk", description=MULTILINE)])
    parsed = yaml.safe_load(text)
    assert parsed["classes"]["stream_chunk"]["description"] == MULTILINE
