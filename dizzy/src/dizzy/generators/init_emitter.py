"""Init emitter — writes empty __init__.py in every generated directory."""

from pathlib import Path

from dizzy.generators.paths import gen_def_root, gen_int_root
from dizzy.logger import logger


def write_init_files(output_dir: Path) -> None:
    """Write an empty __init__.py in every directory of the gen_def/ and gen_int/ packages."""
    for root in (gen_def_root(output_dir), gen_int_root(output_dir)):
        if not root.exists():
            continue
        for dirpath in sorted(root.rglob("*")):
            if dirpath.is_dir():
                init = dirpath / "__init__.py"
                if not init.exists():
                    init.write_text("")
                    logger.debug("wrote %s", init)
        # also write at the package root level
        root_init = root / "__init__.py"
        if not root_init.exists():
            root_init.write_text("")
            logger.debug("wrote %s", root_init)
