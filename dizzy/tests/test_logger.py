"""Tests for the dizzy logging setup."""

import json
import logging
from pathlib import Path

import pytest

from dizzy.logger import logger, setup_logging


def test_setup_logging_creates_log_file(tmp_path: Path) -> None:
    setup_logging(log_dir=tmp_path)
    assert (tmp_path / "dizzy.log").exists()


def test_info_captured_by_caplog(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="dizzy"):
        logger.info("hello from dizzy")
    assert "hello from dizzy" in caplog.text


def test_debug_writes_json_to_file(tmp_path: Path) -> None:
    # Re-create a fresh logger with only the file handler to avoid cross-test pollution
    test_logger = logging.getLogger("dizzy.test_debug_json")
    test_logger.setLevel(logging.DEBUG)
    test_logger.propagate = False

    log_file = tmp_path / "dizzy.log"
    from dizzy.logger import _JsonFormatter
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(_JsonFormatter())
    test_logger.addHandler(handler)

    try:
        test_logger.debug("test message", extra={"key": "val"})
    finally:
        handler.close()
        test_logger.removeHandler(handler)

    line = log_file.read_text().strip()
    record = json.loads(line)
    assert record["msg"] == "test message"
    assert record["key"] == "val"
    assert record["level"] == "DEBUG"
