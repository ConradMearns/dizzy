"""Run the generated agent lib for a single turn, streaming to the CLI.

This is the *host*: it supplies the interstitial infrastructure DIZZY leaves
open — an in-memory event log, the emit/query closures, the injected LLM config
(environment), and the telemetry sink — then invokes the `run_agent_turn`
procedure exactly as a real runtime would.

    python demo.py            # uses the pre-made message below
    python demo.py "hi there" # or pass your own
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Make the generated workspace packages importable without `uv sync`.
HERE = Path(__file__).parent
LIB = HERE / "lib" / "python-uv"
for sub in ("gen_def", "gen_int", "procedure/run_agent_turn/src"):
    sys.path.insert(0, str(LIB / sub))

load_dotenv(HERE / ".env")

from gen_def.pydantic.commands import SendMessage
from gen_def.pydantic.environment import Llm
from gen_def.pydantic.events import UserMessageSent, AgentReplied
from gen_def.pydantic.query.get_conversation import (
    GetConversationInput,
    GetConversationOutput,
)
from gen_int.python.procedure.run_agent_turn_context import (
    run_agent_turn_context,
    run_agent_turn_emitters,
    run_agent_turn_env,
    run_agent_turn_queries,
    run_agent_turn_telemetry,
)
from run_agent_turn import run_agent_turn

MODEL = os.getenv("OPENAI_MODEL", "google/gemma-4-26b-a4b-it")
SESSION_ID = "demo-session"

# ── The event log: the source of truth the host owns ──────────────────────
EVENTS: list = []


# ── emit closures: append immutable facts to the log ──────────────────────
def emit_event(event) -> None:
    EVENTS.append(event)


# ── query closure: an inline projection folding events for one session ────
def get_conversation(inp: GetConversationInput) -> GetConversationOutput:
    roles, contents, created_ats, total_tokens = [], [], [], []
    for e in EVENTS:
        if e.session_id != inp.session_id:
            continue
        if isinstance(e, UserMessageSent):
            roles.append("user")
            contents.append(e.content)
            created_ats.append(e.sent_at)
            total_tokens.append(0)
        elif isinstance(e, AgentReplied):
            roles.append("assistant")
            contents.append(e.content)
            created_ats.append(e.replied_at)
            total_tokens.append(e.total_tokens or 0)
    return GetConversationOutput(
        roles=roles,
        contents=contents,
        created_ats=created_ats,
        total_tokens=total_tokens,
    )


# ── telemetry sink: stream chunks live to the CLI, capture usage ──────────
captured = {}


def stream_chunk(chunk) -> None:
    if chunk.text:
        print(chunk)
        return
        print(chunk.text, end="", flush=True)
    if chunk.usage is not None:
        captured["usage"] = chunk.usage


def build_context() -> run_agent_turn_context:
    return run_agent_turn_context(
        emit=run_agent_turn_emitters(
            user_message_sent=emit_event,
            agent_replied=emit_event,
        ),
        query=run_agent_turn_queries(get_conversation=get_conversation),
        env=run_agent_turn_env(
            llm=Llm(
                model=MODEL,
                api_key=os.environ["OPENAI_API_KEY"],
                base_url=os.environ["OPENAI_API_BASE"],
            )
        ),
        telemetry=run_agent_turn_telemetry(stream_chunk=stream_chunk),
    )


def main() -> None:
    message = sys.argv[1] if len(sys.argv) > 1 else "What is the meaning of life?"
    print(f">>> {message}\n")

    run_agent_turn(
        build_context(),
        SendMessage(session_id=SESSION_ID, role="user", content=message),
    )
    print()

    usage = captured.get("usage")
    if usage:
        print("\n──── telemetry ────")
        print(f"prompt     : {usage.prompt_tokens:>8} tokens")
        print(f"completion : {usage.completion_tokens:>8} tokens")
        print(f"total      : {usage.total_tokens:>8} tokens")

    # The durable facts the turn recorded (the event stream is the truth).
    print(f"\n[events] recorded {len(EVENTS)}: {[type(e).__name__ for e in EVENTS]}")


if __name__ == "__main__":
    main()
