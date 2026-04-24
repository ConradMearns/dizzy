"""Dizzy configuration — layered YAML config merged system → user → project."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class LoggingConfig(BaseModel):
    log_dir: Path | None = None
    show_level: bool = False
    gitignore: bool = True


class DizzyConfig(BaseModel):
    logging: LoggingConfig = LoggingConfig()


_CONFIG_PATHS = [
    Path("/etc/dizzy/config.yaml"),
    Path.home() / ".config" / "dizzy" / "config.yaml",
    Path(".dizzy.yaml"),
]

CONFIG_TEMPLATE = """\
# Dizzy configuration
# Place this file at one of:
#   .dizzy.yaml                      — project-level (current directory)
#   ~/.config/dizzy/config.yaml      — user-level
#   /etc/dizzy/config.yaml           — system-level
#
# Higher-precedence files override lower ones.
# Environment variables override everything.

logging:
  # Directory where debug JSON log files are written.
  # Default: ~/.local/share/dizzy/logs
  # Override with env var: DIZZY_LOG_DIR
  # log_dir: ~/.local/share/dizzy/logs

  # Show the log level prefix (INFO/WARNING/ERROR) in terminal output.
  # Default: false
  # show_level: false

  # Write a .gitignore containing "*" in the log directory on each invocation.
  # Default: true
  # gitignore: true
"""


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config() -> DizzyConfig:
    """Merge configs from system → user → project, then apply env var overrides."""
    merged: dict[str, Any] = {}
    for path in _CONFIG_PATHS:
        if path.exists():
            raw = yaml.safe_load(path.read_text()) or {}
            merged = _deep_merge(merged, raw)

    config = DizzyConfig.model_validate(merged)

    if log_dir := os.environ.get("DIZZY_LOG_DIR"):
        config.logging.log_dir = Path(log_dir)

    return config
