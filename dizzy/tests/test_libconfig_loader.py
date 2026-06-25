"""Tests for libconfig_loader — load_libconfig and validate_libconfig."""

import textwrap
from pathlib import Path

import pytest
from dizzy.feat_schema import FeatureDefinition
from dizzy.libconfig_loader import load_libconfig, validate_libconfig
from dizzy.libconfig_schema import LanguageRuntime
from pydantic import ValidationError


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "libconfig.yaml"
    p.write_text(textwrap.dedent(content))
    return p


def test_load_empty(tmp_path: Path) -> None:
    p = _write(tmp_path, "")
    config = load_libconfig(p)
    assert config.procedures == []
    assert config.policies == []
    assert config.queries == []
    assert config.projections == []


def test_load_dict_key_shorthand(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        """
        procedures:
          my_proc:
            runtimes: [python-uv, rust-cargo]
        """,
    )
    config = load_libconfig(p)
    assert config.procedures is not None
    assert len(config.procedures) == 1
    binding = config.procedures[0]
    assert binding.name == "my_proc"
    assert binding.runtimes is not None
    assert LanguageRuntime.python_uv in binding.runtimes
    assert LanguageRuntime.rust_cargo in binding.runtimes


def test_load_list_shorthand(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        """
        policies:
          my_policy: [typescript-npm]
        """,
    )
    config = load_libconfig(p)
    assert config.policies is not None
    assert len(config.policies) == 1
    assert config.policies[0].runtimes == [LanguageRuntime.typescript_npm]


def test_load_empty_runtimes(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        """
        procedures:
          my_proc:
            runtimes: []
        """,
    )
    config = load_libconfig(p)
    assert config.procedures is not None
    assert config.procedures[0].runtimes == []


def test_validate_unknown_procedure(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        """
        procedures:
          nonexistent:
            runtimes: [python-uv]
        """,
    )
    config = load_libconfig(p)
    feat = FeatureDefinition.model_validate({"procedures": []})
    errors = validate_libconfig(config, feat)
    assert any("nonexistent" in e for e in errors)


def test_validate_valid_references(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        """
        procedures:
          my_proc:
            runtimes: [python-uv]
        policies:
          my_policy:
            runtimes: [typescript-npm]
        """,
    )
    config = load_libconfig(p)
    feat = FeatureDefinition.model_validate(
        {
            "procedures": [{"name": "my_proc", "command": "cmd", "description": "d"}],
            "policies": [{"name": "my_policy", "event": "evt", "description": "d"}],
        }
    )
    errors = validate_libconfig(config, feat)
    assert errors == []


def test_load_invalid_runtime(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        """
        procedures:
          my_proc:
            runtimes: [not-a-runtime]
        """,
    )
    with pytest.raises(ValidationError):
        load_libconfig(p)
