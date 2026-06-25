#!/usr/bin/env python3
"""Regenerate a tutorial's asset files from a canonical worked example.

A validated tutorial (``docs/tutorials/<name>.md``) applies a sequence of patches to
files that ``dizzy generate`` scaffolds. Hand-maintaining those patches is tedious and
drifts. Instead, the worked example under ``examples/<name>/`` is the source of truth:
you edit it, run this script, and it re-derives the tutorial's assets:

* whole files the reader authors verbatim (the feature-file, ``demo.py``) are copied
  into the asset dir;
* every author edit to a *generated* file is captured as a unified diff under
  ``edits/``, by running the real generation pipeline in a throwaway git repo and
  diffing the scaffold/stub against the example.

The author edits in two phases, mirroring the tutorial:

1. ``generate definitions`` scaffolds ``def/**.yaml`` → diff scaffold vs example.
2. ``generate static`` + ``generate libraries`` scaffold the ``src/*.py`` stubs →
   diff stub vs example.

Usage:
    python scripts/capture_tutorial.py guestbook
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _dizzy(stage: str, feat: str, cwd: Path) -> None:
    _run(["uv", "run", "--project", str(REPO), "dizzy", "generate", stage, feat, "."], cwd)


def _git(args: list[str], cwd: Path, capture: bool = False) -> str:
    res = subprocess.run(
        ["git", *args], cwd=cwd, check=True, text=True,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
    )
    return res.stdout if capture else ""


def _write_diffs(sandbox: Path, rel_paths: list[Path], edits: Path) -> list[str]:
    """For each changed file, write a clean unified diff to edits/<basename>.diff."""
    written: list[str] = []
    for rel in rel_paths:
        raw = _git(["diff", "--", str(rel)], sandbox, capture=True)
        if not raw.strip():
            continue
        # Strip git's `diff --git`/`index` preamble so the rendered diff is a plain,
        # readable unified diff. `git apply` still accepts the `--- a/ +++ b/` form.
        lines = raw.splitlines(keepends=True)
        start = next(i for i, ln in enumerate(lines) if ln.startswith("--- "))
        name = f"{rel.name}.diff"
        (edits / name).write_text("".join(lines[start:]))
        written.append(name)
    return written


def capture(name: str) -> None:
    example = REPO / "examples" / name
    feat = f"{name}.feat.yaml"
    out = REPO / "docs" / "tutorials" / name
    edits = out / "edits"
    if not (example / feat).exists():
        sys.exit(f"no example feature-file at {example / feat}")
    edits.mkdir(parents=True, exist_ok=True)

    # Whole-file assets the reader creates verbatim (shown as copyable code blocks).
    for asset in (feat, "demo.py"):
        src = example / asset
        if src.exists():
            shutil.copy(src, out / asset)

    written: list[str] = []
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        shutil.copy(example / feat, tmp / feat)
        if (example / "libconfig.yaml").exists():
            shutil.copy(example / "libconfig.yaml", tmp / "libconfig.yaml")

        # Phase 1: scaffold def/ → capture the schema edits.
        _dizzy("definitions", feat, tmp)
        _git(["init", "-q"], tmp)
        _git(["add", "-A"], tmp)
        _git(["commit", "-qm", "scaffold"], tmp)

        def_files = sorted((example / "def").rglob("*.yaml"))
        for f in def_files:
            shutil.copy(f, tmp / f.relative_to(example))
        written += _write_diffs(tmp, [f.relative_to(example) for f in def_files], edits)
        _git(["add", "-A"], tmp)
        _git(["commit", "-qm", "fill def"], tmp)

        # Phase 2: scaffold the src/ stubs → capture the implementation edits.
        _dizzy("static", feat, tmp)
        _dizzy("libraries", feat, tmp)
        _git(["add", "-A"], tmp)
        _git(["commit", "-qm", "scaffold stubs"], tmp)

        impl_files = [
            f for f in sorted((example / "lib").rglob("src/*.py"))
            if not any(p in f.parts for p in ("gen_def", "gen_int", ".venv"))
        ]
        for f in impl_files:
            shutil.copy(f, tmp / f.relative_to(example))
        written += _write_diffs(tmp, [f.relative_to(example) for f in impl_files], edits)

    # Drop stale diffs that no longer correspond to an edit.
    for old in edits.glob("*.diff"):
        if old.name not in written:
            old.unlink()

    print(f"captured {len(written)} diffs + assets into {out.relative_to(REPO)}/")
    for n in written:
        print(f"  edits/{n}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/capture_tutorial.py <example-name>")
    capture(sys.argv[1])
