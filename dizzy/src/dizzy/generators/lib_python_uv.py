"""Python-uv runtime generator — generates lib/python-uv/ package structure."""

from pathlib import Path

from dizzy.feat_schema import PolicyDef, ProcedureDef, ProjectionDef, QueryDef
from dizzy.generators.policies import render_src_policy_stub
from dizzy.generators.procedures import render_src_procedure_stub
from dizzy.generators.projections import render_src_projection_stub
from dizzy.logger import logger


def render_element_pyproject_toml(kind: str, name: str) -> str:
    return "\n".join([
        "[project]",
        f'name = "{kind}-{name}"',
        'version = "0.1.0"',
        'requires-python = ">=3.11"',
        "",
        "[build-system]",
        'requires = ["hatchling"]',
        'build-backend = "hatchling.build"',
        "",
    ])


def render_workspace_pyproject_toml(members: list[tuple[str, str]]) -> str:
    member_lines = "\n".join(f'  "{kind}/{name}",' for kind, name in members)
    return "\n".join([
        "[tool.uv.workspace]",
        "members = [",
        member_lines,
        "]",
        "",
    ])


def _write_if_absent(path: Path, content: str) -> None:
    if path.exists():
        logger.debug("skipped existing file", extra={"path": str(path)})
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    logger.debug("wrote file", extra={"path": str(path)})


def write_procedure_python_uv(proc: ProcedureDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "python-uv" / "procedure" / proc.name
    _write_if_absent(base / "pyproject.toml", render_element_pyproject_toml("procedure", proc.name))
    _write_if_absent(base / "src" / f"{proc.name}.py", render_src_procedure_stub(proc))


def write_policy_python_uv(policy: PolicyDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "python-uv" / "policy" / policy.name
    _write_if_absent(base / "pyproject.toml", render_element_pyproject_toml("policy", policy.name))
    _write_if_absent(base / "src" / f"{policy.name}.py", render_src_policy_stub(policy))


def write_query_python_uv(query: QueryDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "python-uv" / "query" / query.name
    _write_if_absent(base / "pyproject.toml", render_element_pyproject_toml("query", query.name))
    stub = "\n".join([
        "# Implementation stub — fill in your logic here",
        f"from gen_int.python.query.{query.name} import {query.name}_query",
        "",
        "",
        f"def {query.name}() -> None:",
        "    raise NotImplementedError",
        "",
    ])
    _write_if_absent(base / "src" / f"{query.name}.py", stub)


def write_projection_python_uv(proj: ProjectionDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "python-uv" / "projection" / proj.name
    _write_if_absent(base / "pyproject.toml", render_element_pyproject_toml("projection", proj.name))
    _write_if_absent(base / "src" / f"{proj.name}.py", render_src_projection_stub(proj))


def write_workspace_python_uv(members: list[tuple[str, str]], output_dir: Path) -> None:
    dest = output_dir / "lib" / "python-uv" / "pyproject.toml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_workspace_pyproject_toml(members))
    logger.debug("wrote file", extra={"path": str(dest)})
