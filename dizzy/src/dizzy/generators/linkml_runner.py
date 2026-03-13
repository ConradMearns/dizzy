"""LinkML runner — shells out to gen-pydantic / gen-sqla to produce gen_def/ files."""

import subprocess
from pathlib import Path


def run_linkml_pydantic(def_file: Path, output_file: Path) -> None:
    """Run gen-pydantic on def_file and write the result to output_file."""
    result = subprocess.run(
        ["gen-pydantic", str(def_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(result.stdout)


def run_linkml_sqla(def_file: Path, output_file: Path) -> None:
    """Run gen-sqla on def_file and write the result to output_file."""
    result = subprocess.run(
        ["gen-sqla", str(def_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(result.stdout)
