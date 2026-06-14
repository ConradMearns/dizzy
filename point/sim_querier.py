# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""sim_querier spike (point/EXECUTORS.md "Axis 3", seed dizzy-6018) — the jmQ collapse
(PLAN rule 10): answer a query from the EVENT STREAM alone. Agent-spawn plumbing lives
in point/agent.py; this file builds the querier prompt and applies the resolved protocol.

Querier tool stack = [answer, report_finding] (PLAN § Query evaluation):
  * answer(answer)        — the result, derived from the stream (success)
  * report_finding(...)   — the stream genuinely cannot answer (rule 10 failure mode)
  * NEITHER (no tool call) — a NULL response; the harness synthesizes a
                             null-query-response finding (a query that returns nothing is
                             itself a problem, never an empty answer).

Run:  uv run point/sim_querier.py
      uv run point/sim_querier.py --query get_next_reservation --args "who is next for SICP?"
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent  # noqa: E402

DEFAULT_FEAT = Path(__file__).resolve().parent / "library.feat.yaml"

# A small hand-authored event stream (narrative facts to date) the querier reasons over.
DEFAULT_STREAM = [
    "member_registered: Ada, member id 0042-02-00000001, minted at Front Desk",
    'book_added: "Structure and Interpretation of Computer Programs" (SICP), 1 copy',
    "book_reserved: Grace joined the reservation queue for SICP",
]

SYSTEM_PROMPT = (
    "You are a QUERIER in an event-sourced system (the jmQ collapse). Answer the query "
    "using ONLY the event stream provided — it is the single source of truth; there are "
    "no other facts and no database. Do not invent or assume anything not derivable from "
    "the stream. Call exactly one tool: `answer` with a concise, direct result derived "
    "from the stream, or `report_finding` if the stream genuinely cannot answer. Do not "
    "reply in prose — always call a tool."
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
        f"Answer the query from the stream above by calling `answer` or `report_finding`."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=list(agent.DEFAULT_MODELS), default="claude")
    parser.add_argument("--model", default=None)
    parser.add_argument("--feat", type=Path, default=DEFAULT_FEAT)
    parser.add_argument("--query", default="get_book_availability")
    parser.add_argument("--args", default="How many copies of SICP are available to borrow?")
    args = parser.parse_args()

    description = load_query(args.feat, args.query)
    tools = [agent.ToolSpec("answer", "answer"), agent.ToolSpec("report_finding", "finding")]

    print(f"=== querier {args.query} via {args.engine} ===", file=sys.stderr)
    result = agent.run_activation(
        engine=args.engine, model=args.model, system_prompt=SYSTEM_PROMPT,
        user_prompt=build_user_prompt(args.query, description, args.args, DEFAULT_STREAM),
        tools=tools,
    )

    answers = result.of_kind("answer")
    findings = result.of_kind("finding")

    if answers:
        print("=== answer ===")
        print(answers[0]["args"]["answer"])
    elif findings:
        print("=== report_finding (stream could not answer) ===")
        print(json.dumps(findings[0]["args"]))
    else:
        # NULL response → the harness files the finding itself (PLAN § Query evaluation).
        print("=== null-query-response (synthesized finding) ===")
        print(json.dumps({"category": "null-query-response", "query": args.query,
                          "detail": "querier ended its turn without calling answer or report_finding"}))

    sys.exit(0 if (answers or findings) else 1)


if __name__ == "__main__":
    main()
