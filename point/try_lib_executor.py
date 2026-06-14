# /// script
# requires-python = ">=3.11"
# dependencies = ["fastapi>=0.110", "uvicorn>=0.29", "pyyaml>=6.0"]
# ///
"""lib_executor spike (point/EXECUTORS.md, seed dizzy-cc49) — the real-code mirror of
try_sim_executor. Instead of spawning an LLM that PLAYS a component, it runs the
component's REAL generated handler code (trigger in, emissions out).

Same contract as try_sim_executor: execute(component, trigger) -> emissions. The
component calls back out to record each emission — but where the LLM path needs MCP
tool-calling, real handler code only needs a plain RPC, so the emit sink here is a
local FastAPI HTTP endpoint (the cross-language lingua franca; a Rust/TS handler can
POST to it too). The handler runs in its own uv env via lib_runner.py (language behind
the subprocess boundary); its emit.<name> callbacks POST to the sink, recorded here.

Run (after generating + uv-syncing the lib under --lib):
  uv run point/try_lib_executor.py --component catalog_book --payload '{"title":"SICP","copies":1}'
  uv run point/try_lib_executor.py --component index_on_catalog \
      --payload '{"catalog_id":"abc","title":"SICP","copies":1}'
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI, Request

HERE = Path(__file__).resolve().parent
DEFAULT_FEAT = HERE / "lib_min" / "lib_min.feat.yaml"
DEFAULT_LIB = HERE / "lib_min" / "lib" / "python-uv"
RUNNER = HERE / "lib_runner.py"


def camelcase(snake: str) -> str:
    return "".join(p.capitalize() for p in snake.split("_"))


# ================================================================================
# feat -> runner spec (which generated modules/classes realize this component)
# ================================================================================
def build_spec(feat_path: Path, name: str, payload: dict, sink_url: str) -> dict:
    feat = yaml.safe_load(feat_path.read_text())
    if name in feat.get("procedures", {}):
        c = feat["procedures"][name]
        return {
            "signature": "procedure", "out_kind": "emit", "queries": c.get("queries", []),
            "handler_module": name, "handler_func": name,
            "context_module": f"gen_int.python.procedure.{name}_context",
            "context_class": f"{name}_context", "emitters_class": f"{name}_emitters",
            "input_module": "gen_def.pydantic.commands", "input_class": camelcase(c["command"]),
            "payload": payload, "sink_url": sink_url,
        }
    if name in feat.get("policies", {}):
        c = feat["policies"][name]
        return {
            "signature": "policy", "out_kind": "dispatch", "queries": c.get("queries", []),
            "handler_module": name, "handler_func": name,
            "context_module": f"gen_int.python.policy.{name}_context",
            "context_class": f"{name}_context", "emitters_class": f"{name}_emitters",
            "input_module": "gen_def.pydantic.events", "input_class": camelcase(c["event"]),
            "payload": payload, "sink_url": sink_url,
        }
    raise SystemExit(f"component {name!r} not found in {feat_path} (procedures/policies)")


# ================================================================================
# the FastAPI emit sink (parent process)
# ================================================================================
def start_sink() -> tuple[list[dict], uvicorn.Server, str]:
    """Stand up an HTTP emit endpoint on a free port; return (recorded, server, url)."""
    recorded: list[dict] = []
    app = FastAPI()

    @app.post("/emit")
    async def emit(request: Request) -> dict:
        recorded.append(await request.json())
        return {"ok": True}

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:  # wait for bind before spawning the runner
        time.sleep(0.02)
    return recorded, server, f"http://127.0.0.1:{port}/emit"


# ================================================================================
# parent mode — run the real handler via lib_runner in the lib's uv env
# ================================================================================
def drive(feat: Path, lib: Path, component: str, payload: dict) -> None:
    recorded, server, sink_url = start_sink()
    spec = build_spec(feat, component, payload, sink_url)

    print(f"=== {component} ({spec['signature']}) via real lib code ===", file=sys.stderr)
    print(f"=== sink: {sink_url}  out_kind: {spec['out_kind']} ===", file=sys.stderr)

    # Boundary: query-bearing components need a lib_querier (deployed model + projections),
    # which is deferred (point/EXECUTORS.md "lib_querier needs deployment planning"). Report
    # a clean finding instead of crashing on the unwired context.query field.
    if spec["queries"]:
        server.should_exit = True
        print("\n=== recorded emissions ===")
        print(json.dumps({"finding": True, "error": (
            f"{component} declares queries {spec['queries']} — lib_querier not implemented "
            "yet (needs a deployed model + projections; see EXECUTORS.md, seed dizzy-4ed2). "
            "Only emit/dispatch-only components run under try_lib_executor today."
        )}))
        sys.exit(1)

    # Drop VIRTUAL_ENV so uv doesn't warn about our PEP723 env vs the lib's .venv.
    child_env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    proc = subprocess.run(
        ["uv", "run", "--project", str(lib), "python", str(RUNNER), json.dumps(spec)],
        capture_output=True, text=True, timeout=120, env=child_env,
    )
    server.should_exit = True

    if proc.stderr.strip():
        print("=== runner stderr ===", file=sys.stderr)
        print(proc.stderr.strip(), file=sys.stderr)

    print("\n=== recorded emissions ===")
    if recorded:
        for entry in recorded:
            print(json.dumps(entry))
    else:
        print("(none — handler emitted nothing)")

    sys.exit(0 if (recorded and proc.returncode == 0) else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--feat", type=Path, default=DEFAULT_FEAT)
    parser.add_argument("--lib", type=Path, default=DEFAULT_LIB)
    parser.add_argument("--component", default="catalog_book")
    parser.add_argument("--payload", default='{"title":"SICP","copies":1}',
                        help="JSON payload for the triggering command (procedure) or event (policy)")
    args = parser.parse_args()
    drive(args.feat, args.lib, args.component, json.loads(args.payload))
