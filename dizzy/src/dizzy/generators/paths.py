"""Output-path helpers for the lib/-only layout.

Generated python code (``gen_def`` / ``gen_int``) and the per-element packages all
live under ``lib/python-uv/`` so each runtime tree is self-contained. ``gen_def`` and
``gen_int`` are installable uv packages: their *project* directory (the one holding
``pyproject.toml``) wraps an importable package directory of the same name, so the
import names ``gen_def`` / ``gen_int`` used throughout the generated code keep working.
"""

from pathlib import Path


def lib_python_uv_dir(output_dir: Path) -> Path:
    """The python-uv runtime workspace root (holds the workspace pyproject.toml)."""
    return output_dir / "lib" / "python-uv"


def gen_def_pkg_dir(output_dir: Path) -> Path:
    """gen_def *project* directory — holds its pyproject.toml."""
    return lib_python_uv_dir(output_dir) / "gen_def"


def gen_def_root(output_dir: Path) -> Path:
    """Importable ``gen_def`` package root (``.../gen_def/gen_def``)."""
    return gen_def_pkg_dir(output_dir) / "gen_def"


def gen_int_pkg_dir(output_dir: Path) -> Path:
    """gen_int *project* directory — holds its pyproject.toml."""
    return lib_python_uv_dir(output_dir) / "gen_int"


def gen_int_root(output_dir: Path) -> Path:
    """Importable ``gen_int`` package root (``.../gen_int/gen_int``)."""
    return gen_int_pkg_dir(output_dir) / "gen_int"
