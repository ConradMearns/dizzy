"""Tests for the dizzy configuration loader."""

from pathlib import Path

import pytest
from dizzy.config import load_config


def test_defaults_when_no_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DIZZY_LOG_DIR", raising=False)
    config = load_config()
    assert config.logging.log_dir is None


def test_project_config_sets_log_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DIZZY_LOG_DIR", raising=False)
    (tmp_path / ".dizzy.yaml").write_text("logging:\n  log_dir: /tmp/dizzy-logs\n")
    config = load_config()
    assert config.logging.log_dir == Path("/tmp/dizzy-logs")


def test_env_var_overrides_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".dizzy.yaml").write_text("logging:\n  log_dir: /tmp/from-file\n")
    monkeypatch.setenv("DIZZY_LOG_DIR", "/tmp/from-env")
    config = load_config()
    assert config.logging.log_dir == Path("/tmp/from-env")


def test_higher_precedence_file_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DIZZY_LOG_DIR", raising=False)
    user_config = tmp_path / "user_config.yaml"
    user_config.write_text("logging:\n  log_dir: /tmp/user-logs\n")
    project_config = tmp_path / ".dizzy.yaml"
    project_config.write_text("logging:\n  log_dir: /tmp/project-logs\n")

    # Patch _CONFIG_PATHS to use our temp files in order
    import dizzy.config as cfg_module

    original = cfg_module._CONFIG_PATHS
    cfg_module._CONFIG_PATHS = [user_config, project_config]
    try:
        config = load_config()
    finally:
        cfg_module._CONFIG_PATHS = original

    assert config.logging.log_dir == Path("/tmp/project-logs")
