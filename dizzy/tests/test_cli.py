"""End-to-end def + gen integration tests."""

import pytest
from click.exceptions import Exit as ClickExit
from pathlib import Path

from dizzy.cli import def_cmd, gen

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_def_creates_def_stubs(tmp_path: Path) -> None:
    def_cmd(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    assert (tmp_path / "def" / "commands.yaml").exists()
    assert (tmp_path / "def" / "events.yaml").exists()
    assert (tmp_path / "def" / "queries" / "get_recipe_text.yaml").exists()
    assert (tmp_path / "def" / "queries" / "get_recipe.yaml").exists()
    assert (tmp_path / "def" / "models" / "recipes.yaml").exists()


def test_def_does_not_overwrite(tmp_path: Path) -> None:
    def_cmd(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    commands_path = tmp_path / "def" / "commands.yaml"
    original_content = commands_path.read_text()
    commands_path.write_text("# custom content\n")

    def_cmd(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    assert commands_path.read_text() == "# custom content\n"
    assert (tmp_path / "def" / "events.yaml").read_text() != "# custom content\n"


def test_gen_creates_all_outputs(tmp_path: Path) -> None:
    def_cmd(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)
    gen(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    # gen_def/ — linkml outputs
    assert (tmp_path / "gen_def" / "pydantic" / "commands.py").exists()
    assert (tmp_path / "gen_def" / "pydantic" / "events.py").exists()
    assert (tmp_path / "gen_def" / "pydantic" / "query" / "get_recipe_text.py").exists()
    assert (tmp_path / "gen_def" / "pydantic" / "query" / "get_recipe.py").exists()
    assert (tmp_path / "gen_def" / "pydantic" / "models" / "recipes.py").exists()
    assert (tmp_path / "gen_def" / "sqla" / "models" / "recipes.py").exists()

    # gen_int/ — protocol outputs
    assert (tmp_path / "gen_int" / "python" / "query" / "get_recipe_text.py").exists()
    assert (tmp_path / "gen_int" / "python" / "query" / "get_recipe.py").exists()
    assert (tmp_path / "gen_int" / "python" / "procedure" / "extract_and_transform_recipe_context.py").exists()
    assert (tmp_path / "gen_int" / "python" / "procedure" / "extract_and_transform_recipe_protocol.py").exists()
    assert (tmp_path / "gen_int" / "python" / "policy" / "index_recipe_on_ingest_context.py").exists()
    assert (tmp_path / "gen_int" / "python" / "policy" / "index_recipe_on_ingest_protocol.py").exists()
    assert (tmp_path / "gen_int" / "python" / "projection" / "recipe_library_projection.py").exists()

    # src/ — implementation stubs
    assert (tmp_path / "src" / "query" / "get_recipe_text.py").exists()
    assert (tmp_path / "src" / "query" / "get_recipe.py").exists()
    assert (tmp_path / "src" / "procedure" / "extract_and_transform_recipe.py").exists()
    assert (tmp_path / "src" / "policy" / "index_recipe_on_ingest.py").exists()
    assert (tmp_path / "src" / "projection" / "recipe_library.py").exists()

    # __init__.py in every generated directory
    assert (tmp_path / "gen_def" / "__init__.py").exists()
    assert (tmp_path / "gen_def" / "pydantic" / "__init__.py").exists()
    assert (tmp_path / "gen_def" / "pydantic" / "query" / "__init__.py").exists()
    assert (tmp_path / "gen_def" / "pydantic" / "models" / "__init__.py").exists()
    assert (tmp_path / "gen_def" / "sqla" / "__init__.py").exists()
    assert (tmp_path / "gen_def" / "sqla" / "models" / "__init__.py").exists()
    assert (tmp_path / "gen_int" / "__init__.py").exists()
    assert (tmp_path / "gen_int" / "python" / "__init__.py").exists()
    assert (tmp_path / "gen_int" / "python" / "query" / "__init__.py").exists()
    assert (tmp_path / "gen_int" / "python" / "procedure" / "__init__.py").exists()
    assert (tmp_path / "gen_int" / "python" / "policy" / "__init__.py").exists()
    assert (tmp_path / "gen_int" / "python" / "projection" / "__init__.py").exists()


def test_gen_error_when_def_missing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(ClickExit) as exc_info:
        gen(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)
    assert exc_info.value.exit_code == 1
    captured = capsys.readouterr()
    assert "dizzy def" in captured.out
    assert "def/commands.yaml" in captured.out


def test_gen_does_not_overwrite_src(tmp_path: Path) -> None:
    def_cmd(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)
    gen(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    src_file = tmp_path / "src" / "query" / "get_recipe_text.py"
    src_file.write_text("# my implementation\n")

    gen(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    assert src_file.read_text() == "# my implementation\n"
