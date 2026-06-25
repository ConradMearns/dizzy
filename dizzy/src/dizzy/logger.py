"""Dizzy logging — INFO to stderr via rich, DEBUG to JSON file."""

import json
import logging
import os
import time
from pathlib import Path

from rich.logging import RichHandler

_STANDARD_LOG_FIELDS = frozenset(
    {
        "name",
        "msg",
        "args",
        "created",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "exc_info",
        "exc_text",
        "message",
        "taskName",
    }
)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        data: dict = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.message,
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOG_FIELDS and not key.startswith("_"):
                data[key] = value
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data)


def setup_logging(
    log_dir: Path | None = None, show_level: bool = False, gitignore: bool = True
) -> None:
    """Configure the dizzy logger. Called once from main()."""
    if log_dir is None:
        log_dir = Path.home() / ".local" / "share" / "dizzy" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    if gitignore:
        gi = log_dir / ".gitignore"
        if not gi.exists():
            gi.write_text("*\n")

    root = logging.getLogger("dizzy")
    root.setLevel(logging.DEBUG)

    rich_handler = RichHandler(
        level=logging.INFO, show_path=False, markup=False, show_time=False, show_level=show_level
    )
    root.addHandler(rich_handler)

    log_file = log_dir / f"dizzy_{int(time.time())}_{os.getpid()}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_JsonFormatter())
    root.addHandler(file_handler)


logger = logging.getLogger("dizzy")
