"""TypeScript-npm runtime generator — generates lib/typescript-npm/ package structure."""

import json
from pathlib import Path

from dizzy.feat_schema import PolicyDef, ProcedureDef, ProjectionDef, QueryDef


def render_element_package_json(kind: str, name: str) -> str:
    data = {
        "name": f"@dizzy/{kind}-{name}",
        "version": "0.1.0",
        "main": "dist/index.js",
        "scripts": {"build": "tsc"},
    }
    return json.dumps(data, indent=2) + "\n"


def render_element_tsconfig_json() -> str:
    data = {
        "extends": "../../tsconfig.json",
        "compilerOptions": {
            "outDir": "dist",
            "rootDir": "src",
        },
        "include": ["src"],
    }
    return json.dumps(data, indent=2) + "\n"


def render_workspace_package_json(members: list[tuple[str, str]]) -> str:
    workspaces = [f"{kind}/{name}" for kind, name in members]
    data = {
        "name": "@dizzy/lib",
        "private": True,
        "workspaces": workspaces,
    }
    return json.dumps(data, indent=2) + "\n"


def render_workspace_tsconfig_json() -> str:
    data = {
        "compilerOptions": {
            "target": "ES2020",
            "module": "commonjs",
            "strict": True,
            "esModuleInterop": True,
            "declaration": True,
        },
    }
    return json.dumps(data, indent=2) + "\n"


def render_index_ts_stub(name: str) -> str:
    return "\n".join([
        "// Implementation stub — fill in your logic here",
        f"export function {name}(): void {{",
        '    throw new Error("Not implemented");',
        "}",
        "",
    ])


def _write_if_absent(path: Path, content: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def write_procedure_typescript_npm(proc: ProcedureDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "typescript-npm" / "procedure" / proc.name
    _write_if_absent(base / "package.json", render_element_package_json("procedure", proc.name))
    _write_if_absent(base / "tsconfig.json", render_element_tsconfig_json())
    _write_if_absent(base / "src" / "index.ts", render_index_ts_stub(proc.name))


def write_policy_typescript_npm(policy: PolicyDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "typescript-npm" / "policy" / policy.name
    _write_if_absent(base / "package.json", render_element_package_json("policy", policy.name))
    _write_if_absent(base / "tsconfig.json", render_element_tsconfig_json())
    _write_if_absent(base / "src" / "index.ts", render_index_ts_stub(policy.name))


def write_query_typescript_npm(query: QueryDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "typescript-npm" / "query" / query.name
    _write_if_absent(base / "package.json", render_element_package_json("query", query.name))
    _write_if_absent(base / "tsconfig.json", render_element_tsconfig_json())
    _write_if_absent(base / "src" / "index.ts", render_index_ts_stub(query.name))


def write_projection_typescript_npm(proj: ProjectionDef, output_dir: Path) -> None:
    base = output_dir / "lib" / "typescript-npm" / "projection" / proj.name
    _write_if_absent(base / "package.json", render_element_package_json("projection", proj.name))
    _write_if_absent(base / "tsconfig.json", render_element_tsconfig_json())
    _write_if_absent(base / "src" / "index.ts", render_index_ts_stub(proj.name))


def write_workspace_typescript_npm(members: list[tuple[str, str]], output_dir: Path) -> None:
    base = output_dir / "lib" / "typescript-npm"
    base.mkdir(parents=True, exist_ok=True)
    (base / "package.json").write_text(render_workspace_package_json(members))
    tsconfig = base / "tsconfig.json"
    if not tsconfig.exists():
        tsconfig.write_text(render_workspace_tsconfig_json())
