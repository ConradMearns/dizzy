"""Manifest emitters for the generated ``gen_def`` / ``gen_int`` type packages.

These two packages hold the LinkML-compiled types (``gen_def``) and the typed
Protocols/contexts/adapters (``gen_int``). They are emitted as installable uv
workspace members so element packages can depend on them instead of importing
undeclared top-level modules.
"""

from pathlib import Path

from dizzy.generators.paths import gen_def_pkg_dir, gen_int_pkg_dir
from dizzy.logger import logger


def render_gen_def_pyproject() -> str:
    return "\n".join(
        [
            "[project]",
            'name = "gen_def"',
            'version = "0.1.0"',
            'requires-python = ">=3.11"',
            "dependencies = [",
            '    "pydantic>=2",',
            '    "sqlalchemy>=2",',
            "]",
            "",
            "[build-system]",
            'requires = ["hatchling"]',
            'build-backend = "hatchling.build"',
            "",
        ]
    )


def render_gen_int_pyproject() -> str:
    return "\n".join(
        [
            "[project]",
            'name = "gen_int"',
            'version = "0.1.0"',
            'requires-python = ">=3.11"',
            "dependencies = [",
            '    "gen_def",',
            "]",
            "",
            "[tool.uv.sources]",
            "gen_def = { workspace = true }",
            "",
            "[build-system]",
            'requires = ["hatchling"]',
            'build-backend = "hatchling.build"',
            "",
        ]
    )


def write_type_packages(output_dir: Path) -> None:
    """Write pyproject.toml for the gen_def and gen_int packages (always overwritten)."""
    for pkg_dir, content in [
        (gen_def_pkg_dir(output_dir), render_gen_def_pyproject()),
        (gen_int_pkg_dir(output_dir), render_gen_int_pyproject()),
    ]:
        pkg_dir.mkdir(parents=True, exist_ok=True)
        dest = pkg_dir / "pyproject.toml"
        dest.write_text(content)
        logger.debug("wrote file", extra={"path": str(dest)})
