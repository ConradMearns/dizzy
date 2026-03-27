"""Tests for adapters generator."""

import warnings
from pathlib import Path

from dizzy.generators.adapters import render_adapter, write_adapter


def test_render_adapter_sqla_class_name() -> None:
    result = render_adapter("sqla")
    assert "class SqlaAdapter:" in result


def test_render_adapter_sqla_session_field() -> None:
    result = render_adapter("sqla")
    assert "session: Session" in result


def test_render_adapter_sqla_import() -> None:
    result = render_adapter("sqla")
    assert "from sqlalchemy.orm import Session" in result


def test_render_adapter_sqla_auto_generated() -> None:
    result = render_adapter("sqla")
    assert "# AUTO-GENERATED — do not edit" in result


def test_render_adapter_relative_filesystem_class_name() -> None:
    result = render_adapter("relative_filesystem")
    assert "class RelativeFilesystemAdapter:" in result


def test_render_adapter_relative_filesystem_root_field() -> None:
    result = render_adapter("relative_filesystem")
    assert "root: Path" in result


def test_render_adapter_relative_filesystem_import() -> None:
    result = render_adapter("relative_filesystem")
    assert "from pathlib import Path" in result


def test_write_adapter_creates_file(tmp_path: Path) -> None:
    write_adapter("sqla", tmp_path)
    dest = tmp_path / "gen_int" / "python" / "adapters" / "sqla.py"
    assert dest.exists()
    assert "SqlaAdapter" in dest.read_text()


def test_write_adapter_always_overwrites(tmp_path: Path) -> None:
    dest = tmp_path / "gen_int" / "python" / "adapters" / "sqla.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("old content")
    write_adapter("sqla", tmp_path)
    assert "SqlaAdapter" in dest.read_text()


def test_write_adapter_correct_path_relative_filesystem(tmp_path: Path) -> None:
    write_adapter("relative_filesystem", tmp_path)
    dest = tmp_path / "gen_int" / "python" / "adapters" / "relative_filesystem.py"
    assert dest.exists()
    assert "RelativeFilesystemAdapter" in dest.read_text()


def test_render_adapter_unknown_emits_warning() -> None:
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = render_adapter("unknown_adapter")
        assert len(w) == 1
        assert "Unknown adapter" in str(w[0].message)
    assert result == ""


def test_write_adapter_unknown_does_not_create_file(tmp_path: Path) -> None:
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        write_adapter("unknown_adapter", tmp_path)
    dest = tmp_path / "gen_int" / "python" / "adapters" / "unknown_adapter.py"
    assert not dest.exists()
