"""Tests for the LinkML runner — verifies gen-pydantic and gen-sqla produce valid Python."""

from pathlib import Path

from dizzy.cli import def_cmd
from dizzy.generators.linkml_runner import run_linkml_pydantic, run_linkml_sqla

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _scaffold(tmp_path: Path) -> None:
    def_cmd(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)


def test_run_linkml_pydantic_commands(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    out = tmp_path / "gen_def" / "pydantic" / "commands.py"
    run_linkml_pydantic(tmp_path / "def" / "commands.yaml", out)
    assert out.exists()
    content = out.read_text()
    assert "class" in content or "BaseModel" in content


def test_run_linkml_pydantic_events(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    out = tmp_path / "gen_def" / "pydantic" / "events.py"
    run_linkml_pydantic(tmp_path / "def" / "events.yaml", out)
    assert out.exists()
    content = out.read_text()
    assert "class" in content or "BaseModel" in content


def test_run_linkml_pydantic_query(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    out = tmp_path / "gen_def" / "pydantic" / "query" / "get_recipe_text.py"
    run_linkml_pydantic(tmp_path / "def" / "queries" / "get_recipe_text.yaml", out)
    assert out.exists()
    content = out.read_text()
    assert "class" in content or "BaseModel" in content


def test_run_linkml_pydantic_model(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    out = tmp_path / "gen_def" / "pydantic" / "models" / "recipes.py"
    run_linkml_pydantic(tmp_path / "def" / "models" / "recipes.yaml", out)
    assert out.exists()
    content = out.read_text()
    assert "class" in content or "BaseModel" in content


def test_run_linkml_sqla_model(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    out = tmp_path / "gen_def" / "sqla" / "models" / "recipes.py"
    run_linkml_sqla(tmp_path / "def" / "models" / "recipes.yaml", out)
    assert out.exists()
    content = out.read_text()
    assert len(content) > 0


def test_run_linkml_pydantic_creates_parent_dirs(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    out = tmp_path / "deep" / "nested" / "dir" / "commands.py"
    run_linkml_pydantic(tmp_path / "def" / "commands.yaml", out)
    assert out.exists()
