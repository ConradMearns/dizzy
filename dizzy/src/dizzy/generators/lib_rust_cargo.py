"""Rust-cargo runtime generator — generates lib/rust-cargo/ package structure."""

from pathlib import Path

from dizzy.feat_schema import PolicyDef, ProcedureDef, ProjectionDef, QueryDef


def render_element_cargo_toml(kind: str, name: str) -> str:
    return "\n".join([
        "[package]",
        f'name = "{kind}-{name}"',
        'version = "0.1.0"',
        'edition = "2021"',
        "",
        "[lib]",
        f'name = "{name}"',
        "",
    ])


def render_workspace_cargo_toml(members: list[tuple[str, str]]) -> str:
    member_lines = "\n".join(f'  "{kind}/{name}",' for kind, name in members)
    return "\n".join([
        "[workspace]",
        "members = [",
        member_lines,
        "]",
        "",
    ])


def render_lib_rs_stub(name: str) -> str:
    return "\n".join([
        "// Implementation stub — fill in your logic here",
        f"pub fn {name}() {{",
        "    todo!()",
        "}",
        "",
    ])


def _write_if_absent(path: Path, content: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def write_procedure_rust_cargo(proc: ProcedureDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "rust-cargo" / "procedure" / proc.name
    _write_if_absent(base / "Cargo.toml", render_element_cargo_toml("procedure", proc.name))
    _write_if_absent(base / "src" / "lib.rs", render_lib_rs_stub(proc.name))


def write_policy_rust_cargo(policy: PolicyDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "rust-cargo" / "policy" / policy.name
    _write_if_absent(base / "Cargo.toml", render_element_cargo_toml("policy", policy.name))
    _write_if_absent(base / "src" / "lib.rs", render_lib_rs_stub(policy.name))


def write_query_rust_cargo(query: QueryDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "rust-cargo" / "query" / query.name
    _write_if_absent(base / "Cargo.toml", render_element_cargo_toml("query", query.name))
    _write_if_absent(base / "src" / "lib.rs", render_lib_rs_stub(query.name))


def write_projection_rust_cargo(proj: ProjectionDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "rust-cargo" / "projection" / proj.name
    _write_if_absent(base / "Cargo.toml", render_element_cargo_toml("projection", proj.name))
    _write_if_absent(base / "src" / "lib.rs", render_lib_rs_stub(proj.name))


def write_workspace_rust_cargo(members: list[tuple[str, str]], output_dir: Path) -> None:
    dest = output_dir / "lib" / "rust-cargo" / "Cargo.toml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_workspace_cargo_toml(members))
