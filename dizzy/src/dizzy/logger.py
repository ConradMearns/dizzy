"""Dizzy logging — INFO to stderr via rich, DEBUG to JSON file."""

import json
import logging
from pathlib import Path

from rich.logging import RichHandler

_STANDARD_LOG_FIELDS = frozenset({
    "name", "msg", "args", "created", "filename", "funcName",
    "levelname", "levelno", "lineno", "module", "msecs", "pathname",
    "process", "processName", "relativeCreated", "stack_info",
    "thread", "threadName", "exc_info", "exc_text", "message", "taskName",
})


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


def setup_logging(log_dir: Path | None = None) -> None:
    """Configure the dizzy logger. Called once from main()."""
    if log_dir is None:
        log_dir = Path.home() / ".local" / "share" / "dizzy" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("dizzy")
    root.setLevel(logging.DEBUG)

    rich_handler = RichHandler(level=logging.INFO, show_path=False, markup=False)
    root.addHandler(rich_handler)

    file_handler = logging.FileHandler(log_dir / "dizzy.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_JsonFormatter())
    root.addHandler(file_handler)


logger = logging.getLogger("dizzy")
