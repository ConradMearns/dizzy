# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.2", "pyyaml>=6.0"]
# ///
"""sim_querier spike (point/EXECUTORS.md "Axis 3", seed dizzy-6018, half 1) — the jmQ
collapse (PLAN rule 10) in isolation: answer a query from the EVENT STREAM alone.

No projections, no models — the event store IS the state. We spawn an LLM given the
query's description + its arguments + the full emitted event stream, and it answers
from the stream. If the stream cannot answer, it calls report_finding (the querier's
failure mode, rule 10). The answer is the LLM's final text; a finding is an MCP call.

This is the read-side counterpart to try_sim_executor. Proving it standalone de-risks
half 2: wiring it into try_sim_executor's query_<q> handler for the inline round-trip.

Run:  uv run point/try_sim_querier.py                               # get_book_availability, default stream
      uv run point/try_sim_querier.py --query get_next_reservation --args "who is next for SICP?"
      uv run point/try_sim_querier.py --query get_member_registration --args "is 0042-99-00000009 a member?"
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SERVER_NAME = "sim"
DEFAULT_FEAT = Path(__file__).resolve().parent / "library.feat.yaml"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

# A small hand-authored event stream (narrative facts to date) the querier reasons over.
# Mirrors a mid-scenario store: SICP cataloged with 1 copy, one member, no loans yet.
DEFAULT_STREAM = [
    "member_registered: Ada, member id 0042-02-00000001, minted at Front Desk",
    'book_added: "Structure and Interpretation of Computer Programs" (SICP), 1 copy',
    "book_reserved: Grace joined the reservation queue for SICP",
]


# ================================================================================
# serve mode — ad-hoc FastMCP server exposing ONLY report_finding (the failure mode)
# ================================================================================
def serve() -> None:
    from mcp.server.fastmcp import FastMCP

    calls_path = os.environ.get("SIM_CALLS")
    mcp = FastMCP(SERVER_NAME)

    @mcp.tool()
    def report_finding(category: str, summary: str, detail: str) -> str:
        """Call this ONLY if the event stream cannot answer the query. End your turn after."""
        if calls_path:
            with open(calls_path, "a") as fh:
                fh.write(json.dumps({"category": category, "summary": summary, "detail": detail}) + "\n")
        return "finding recorded; end your turn"

    mcp.run(transport="stdio")


# ================================================================================
# prompt + spawn (the jmQ querier sub-activation)
# ================================================================================
SYSTEM_PROMPT = (
    "You are a QUERIER in an event-sourced system (the jmQ collapse). Answer the query "
    "using ONLY the event stream provided — it is the single source of truth; there are "
    "no other facts and no database. Do not invent or assume anything not derivable from "
    "the stream. If the stream genuinely cannot answer, call report_finding instead of "
    "guessing. Otherwise reply with a single concise, direct answer and nothing else."
)


def load_query(feat_path: Path, name: str) -> str:
    feat = yaml.safe_load(feat_path.read_text())
    queries = feat.get("queries", {})
    if name not in queries:
        raise SystemExit(f"query {name!r} not found in {feat_path} (queries)")
    return (queries[name].get("description") or "").strip()


def build_user_prompt(name: str, description: str, args: str, stream: list[str]) -> str:
    dump = "\n".join(f"  - {e}" for e in stream) if stream else "  (empty — no facts yet)"
    return (
        f"query: {name}\n"
        f"description: {description}\n"
        f"arguments: {args}\n\n"
        f"event stream (all facts to date):\n{dump}\n\n"
        f"Answer the query from the stream above."
    )


def drive(model: str, feat: Path, name: str, args: str, stream: list[str]) -> None:
    script = Path(__file__).resolve()
    description = load_query(feat, name)

    calls_file = Path(tempfile.mkstemp(prefix="sim_finding_", suffix=".jsonl")[1])
    calls_file.write_text("")

    config = {"mcpServers": {SERVER_NAME: {
        "command": "uv", "args": ["run", str(script), "serve"],
        "env": {"SIM_CALLS": str(calls_file)},
    }}}
    cmd = [
        "claude", "-p",
        "--model", model,
        "--output-format", "json",
        "--strict-mcp-config",
        "--mcp-config", json.dumps(config),
        "--allowedTools", f"mcp__{SERVER_NAME}__report_finding",
        "--append-system-prompt", SYSTEM_PROMPT,
        build_user_prompt(name, description, args, stream),
    ]

    print(f"=== querier {name} via claude (model: {model}) ===", file=sys.stderr)
    # Clean temp cwd: skip CLAUDE.md auto-discovery (cost), keep OAuth (see memory).
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                          cwd=Path(tempfile.mkdtemp(prefix="sim_q_")))

    answer = ""
    if proc.stdout.strip():
        try:
            answer = json.loads(proc.stdout).get("result", "").strip()
        except json.JSONDecodeError:
            answer = proc.stdout.strip()

    finding = calls_file.read_text().strip()
    calls_file.unlink(missing_ok=True)

    print("=== answer ===")
    print(answer or "(no answer)")
    if finding:
        print("\n=== report_finding (stream could not answer) ===")
        print(finding)

    # Success = produced an answer OR a finding (both are valid querier outcomes).
    sys.exit(0 if (answer or finding) else 1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--model", default=DEFAULT_MODEL)
        parser.add_argument("--feat", type=Path, default=DEFAULT_FEAT)
        parser.add_argument("--query", default="get_book_availability")
        parser.add_argument("--args", default="How many copies of SICP are available to borrow?")
        args = parser.parse_args()
        drive(args.model, args.feat, args.query, args.args, DEFAULT_STREAM)
