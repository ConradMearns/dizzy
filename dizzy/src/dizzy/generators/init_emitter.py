"""Init emitter — writes empty __init__.py in every generated directory."""

from pathlib import Path


def write_init_files(output_dir: Path) -> None:
    """Write an empty __init__.py in every directory under gen_def/ and gen_int/."""
    for root in (output_dir / "gen_def", output_dir / "gen_int"):
        if not root.exists():
            continue
        for dirpath in sorted(root.rglob("*")):
            if dirpath.is_dir():
                init = dirpath / "__init__.py"
                if not init.exists():
                    init.write_text("")
        # also write at the root level
        root_init = root / "__init__.py"
        if not root_init.exists():
            root_init.write_text("")
