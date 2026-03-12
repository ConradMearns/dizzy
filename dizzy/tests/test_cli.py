"""End-to-end scaffold + gen integration tests."""

from pathlib import Path

from dizzy.cli import scaffold

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_scaffold_creates_def_stubs(tmp_path: Path) -> None:
    scaffold(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    assert (tmp_path / "def" / "commands.yaml").exists()
    assert (tmp_path / "def" / "events.yaml").exists()
    assert (tmp_path / "def" / "queries" / "get_recipe_text.yaml").exists()
    assert (tmp_path / "def" / "queries" / "get_recipe.yaml").exists()
    assert (tmp_path / "def" / "models" / "recipes.yaml").exists()


def test_scaffold_does_not_overwrite(tmp_path: Path) -> None:
    scaffold(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    commands_path = tmp_path / "def" / "commands.yaml"
    original_content = commands_path.read_text()
    commands_path.write_text("# custom content\n")

    scaffold(feat_file=FIXTURES_DIR / "recipe.feat.yaml", output_dir=tmp_path)

    assert commands_path.read_text() == "# custom content\n"
    assert (tmp_path / "def" / "events.yaml").read_text() != "# custom content\n"
