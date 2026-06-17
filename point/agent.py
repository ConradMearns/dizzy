"""point/agent.py — provider-based agent activation via direct API tool calls.

Supports OpenRouter, Ollama, and Unsloth (all OpenAI-compatible). Tools are
synthesized from ToolSpec and executed in-process — no MCP server required.

  run_activation(provider, model, system_prompt, user_prompt, tools, event_store,
                 verbose_stream)
  run_querier(query_name, description, args, event_store, provider, model)
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import openai
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

# ---------------------------------------------------------------------------
# providers
# ---------------------------------------------------------------------------

PROVIDERS: dict[str, dict] = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "default_model": "anthropic/claude-haiku-4-5",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,
        "default_model": "llama3.2",
    },
    "unsloth": {
        "base_url": "http://localhost:2242/v1",
        "api_key_env": "UNSLOTH_API_KEY",
        "default_model": None,
    },
}


def _client(provider: str) -> tuple[openai.OpenAI, str | None]:
    cfg = PROVIDERS.get(provider)
    if cfg is None:
        raise ValueError(f"unknown provider {provider!r} (have: {list(PROVIDERS)})")
    api_key = (os.environ.get(cfg["api_key_env"]) if cfg["api_key_env"] else None) or "no-key"
    return openai.OpenAI(base_url=cfg["base_url"], api_key=api_key), cfg["default_model"]


# ---------------------------------------------------------------------------
# shared types
# ---------------------------------------------------------------------------

@dataclass
class ToolSpec:
    """One synthesized tool. kind ∈ emit | dispatch | query | answer | finding."""
    name: str
    kind: str
    meta: dict | None = None


@dataclass
class ActivationResult:
    calls: list[dict]
    result_text: str
    raw_stdout: str = ""

    def of_kind(self, kind: str) -> list[dict]:
        return [c for c in self.calls if c.get("kind") == kind]


# ---------------------------------------------------------------------------
# tool schema synthesis
# ---------------------------------------------------------------------------

def _tool_schema(spec: ToolSpec) -> dict:
    if spec.kind in ("emit", "dispatch"):
        verb = "Emit" if spec.kind == "emit" else "Dispatch"
        desc = f"{verb} {spec.name}. `narrative`: free-text payload describing the fact/intent."
        params, required = {"narrative": {"type": "string"}}, ["narrative"]
    elif spec.kind == "query":
        desc = f"Run {spec.name}. `narrative`: what you need to know from the event stream."
        params, required = {"narrative": {"type": "string"}}, ["narrative"]
    elif spec.kind == "answer":
        desc = "Return the query result. `answer`: concise, direct answer from the event stream."
        params, required = {"answer": {"type": "string"}}, ["answer"]
    else:  # finding
        desc = "Report a gap instead of healing it (missing/ambiguous/unanswerable)."
        params = {"category": {"type": "string"}, "summary": {"type": "string"}, "detail": {"type": "string"}}
        required = ["category", "summary", "detail"]
    return {"type": "function", "function": {"name": spec.name, "description": desc,
            "parameters": {"type": "object", "properties": params, "required": required}}}


def _kind_for(tool_name: str, tools: list[ToolSpec]) -> str:
    for t in tools:
        if t.name == tool_name:
            return t.kind
    return "unknown"


# ---------------------------------------------------------------------------
# single-turn helpers: streaming and non-streaming both return a message dict
# ---------------------------------------------------------------------------

def _plain_turn(client, model, messages, tool_defs, timeout) -> dict:
    resp = client.chat.completions.create(
        model=model, messages=messages, tools=tool_defs, timeout=timeout,
    )
    return resp.choices[0].message.model_dump(exclude_unset=True)


def _stream_turn(client, model, messages, tool_defs, timeout) -> dict:
    """Stream one turn, printing content and tool-call names/args live to stdout."""
    stream = client.chat.completions.create(
        model=model, messages=messages, tools=tool_defs, timeout=timeout, stream=True,
    )

    content_buf: list[str] = []
    tc_buf: dict[int, dict] = {}  # index → {id, name, args}

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta

        if delta.content:
            sys.stdout.write(delta.content)
            sys.stdout.flush()
            content_buf.append(delta.content)

        if delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tc_buf:
                    tc_buf[idx] = {"id": "", "name": "", "args": ""}
                entry = tc_buf[idx]
                if tc.id:
                    entry["id"] = tc.id
                if tc.function:
                    if tc.function.name:
                        if not entry["name"]:
                            sys.stdout.write(f"\n[tool: {tc.function.name}] ")
                            sys.stdout.flush()
                        entry["name"] += tc.function.name
                    if tc.function.arguments:
                        sys.stdout.write(tc.function.arguments)
                        sys.stdout.flush()
                        entry["args"] += tc.function.arguments

    if content_buf or tc_buf:
        sys.stdout.write("\n")
        sys.stdout.flush()

    msg: dict = {"role": "assistant"}
    if content_buf:
        msg["content"] = "".join(content_buf)
    if tc_buf:
        msg["tool_calls"] = [
            {"id": tc_buf[i]["id"], "type": "function",
             "function": {"name": tc_buf[i]["name"], "arguments": tc_buf[i]["args"]}}
            for i in sorted(tc_buf)
        ]
    return msg


# ---------------------------------------------------------------------------
# activation loop
# ---------------------------------------------------------------------------

TERMINAL_KINDS = {"emit", "dispatch", "finding", "answer"}
MAX_TURNS = 10


def run_activation(
    *,
    provider: str,
    model: str | None,
    system_prompt: str,
    user_prompt: str,
    tools: list[ToolSpec],
    event_store: list[str] | None = None,
    verbose_stream: bool = False,
    timeout: int = 300,
) -> ActivationResult:
    client, default_model = _client(provider)
    model = model or default_model

    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    tool_defs = [_tool_schema(t) for t in tools]
    all_calls: list[dict] = []
    _turn = _stream_turn if verbose_stream else _plain_turn

    for _ in range(MAX_TURNS):
        msg = _turn(client, model, messages, tool_defs, timeout)
        messages.append(msg)

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            break

        tool_results = []
        terminal_hit = False

        for tc in tool_calls:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            kind = _kind_for(name, tools)
            all_calls.append({"tool": name, "kind": kind, "args": args})

            if kind == "query":
                qmeta = next((t.meta for t in tools if t.name == name), None) or {}
                qresult = run_querier(
                    query_name=qmeta.get("query", name),
                    description=qmeta.get("description", ""),
                    args=args.get("narrative", ""),
                    event_store=event_store or [],
                    provider=provider, model=model,
                    verbose_stream=verbose_stream,
                )
                all_calls.append({"tool": name, "kind": "query_answer", "args": qresult})
                content = qresult["answer"] if qresult["outcome"] == "answered" \
                    else f"UNANSWERABLE — {qresult.get('finding', {}).get('summary', '')}"
            else:
                content = f"recorded: {name}"
                if kind in TERMINAL_KINDS:
                    terminal_hit = True

            tool_results.append({"role": "tool", "tool_call_id": tc["id"], "content": content})

        messages.extend(tool_results)
        if terminal_hit:
            break

    last = messages[-1] if messages else {}
    result_text = last.get("content", "") if last.get("role") == "assistant" else ""
    return ActivationResult(calls=all_calls, result_text=result_text or "")


# ---------------------------------------------------------------------------
# querier sub-activation
# ---------------------------------------------------------------------------

QUERIER_SYSTEM_PROMPT = (
    "You are a QUERIER in an event-sourced system. Answer the query using ONLY the "
    "event stream provided — it is the single source of truth. Do not invent or assume "
    "anything not derivable from the stream. Call exactly one tool: `answer` with a "
    "concise, direct result, or `report_finding` if the stream genuinely cannot answer. "
    "Do not reply in prose — always call a tool."
)


def _querier_prompt(query_name: str, description: str, args: str, event_store: list[str]) -> str:
    dump = "\n".join(f"  - {e}" for e in event_store) if event_store else "  (empty — no facts yet)"
    return (
        f"query: {query_name}\ndescription: {description}\narguments: {args}\n\n"
        f"event stream:\n{dump}\n\nAnswer by calling `answer` or `report_finding`."
    )


def run_querier(
    *,
    query_name: str,
    description: str,
    args: str,
    event_store: list[str],
    provider: str = "openrouter",
    model: str | None = None,
    verbose_stream: bool = False,
) -> dict:
    tools = [ToolSpec("answer", "answer"), ToolSpec("report_finding", "finding")]
    result = run_activation(
        provider=provider, model=model,
        system_prompt=QUERIER_SYSTEM_PROMPT,
        user_prompt=_querier_prompt(query_name, description, args, event_store),
        tools=tools, verbose_stream=verbose_stream,
    )
    answers, findings = result.of_kind("answer"), result.of_kind("finding")
    if answers:
        return {"outcome": "answered", "answer": answers[0]["args"]["answer"]}
    if findings:
        return {"outcome": "finding", "finding": findings[0]["args"]}
    return {"outcome": "null"}
