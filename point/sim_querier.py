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

def load_query(feat_path: Path, name: str) -> str:
    feat = yaml.safe_load(feat_path.read_text())
    queries = feat.get("queries", {})
    if name not in queries:
        raise SystemExit(f"query {name!r} not found in {feat_path} (queries)")
    return (queries[name].get("description") or "").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=list(agent.DEFAULT_MODELS), default="claude")
    parser.add_argument("--model", default=None)
    parser.add_argument("--feat", type=Path, default=DEFAULT_FEAT)
    parser.add_argument("--query", default="get_book_availability")
    parser.add_argument("--args", default="How many copies of SICP are available to borrow?")
    args = parser.parse_args()

    description = load_query(args.feat, args.query)

    print(f"=== querier {args.query} via {args.engine} ===", file=sys.stderr)
    res = agent.run_querier(query_name=args.query, description=description, args=args.args,
                            event_store=DEFAULT_STREAM, engine=args.engine, model=args.model)

    if res["outcome"] == "answered":
        print("=== answer ===")
        print(res["answer"])
    elif res["outcome"] == "finding":
        print("=== report_finding (stream could not answer) ===")
        print(json.dumps(res["finding"]))
    else:
        # NULL response → the harness files the finding itself (PLAN § Query evaluation).
        print("=== null-query-response (synthesized finding) ===")
        print(json.dumps({"category": "null-query-response", "query": args.query,
                          "detail": "querier ended its turn without calling answer or report_finding"}))

    sys.exit(0 if res["outcome"] in ("answered", "finding") else 1)


if __name__ == "__main__":
    main()
