# PLAN — provider system & the ad-hoc MCP

How the harness actually *talks to a component*. The PLAN's hook table
(`activate_procedure`, `activate_policy`, `evaluate_query`) all bottom out here.

## The core idea

A component activation = **spawn a Claude that plays one procedure/policy**, give it
*only* its description + the trigger, and let it act. The component does not return
parseable prose for us to interpret — it **calls a tool**. Every consequence a
component can produce (emit an event, dispatch a command, ask a query, report a
finding) is a **tool call** against an ad-hoc MCP server the harness stands up.

```
                        harness process
  ┌───────────────────────────────────────────────────────┐
  │  Harness loop ── SessionLog ── EventStore               │
  │        │                                                │
  │        │ activate(component, trigger)                   │
  │        ▼                                                │
  │   Provider.run_activation(prompt, allowed_tools)        │
  │        │                          ▲  tool results       │
  │        │ spawn                     │  (query answers,    │
  │        ▼                           │   "recorded" acks)  │
  │   ┌──────────────┐   MCP/stdio  ┌──┴───────────────┐     │
  │   │ claude -p … │◀────────────▶│  ad-hoc MCP srv  │     │
  │   └──────────────┘   tool calls └──────────────────┘     │
  │     (subprocess)                  handlers mutate        │
  │                                   EventStore + SessionLog│
  └───────────────────────────────────────────────────────┘
```

Because the MCP tool **handlers run inside the harness process**, a tool call lands
directly back in harness state: `emit_*` appends to the event queue and writes an
`emission` entry; `query_*` runs a querier sub-activation over the event store and
returns the answer *inline* as the tool result; `report_finding` writes a `finding`
and signals the activation to end.

## The Provider abstraction

`Provider` is the seam for *how a component LLM is driven*. One method:

```python
class Provider(Protocol):
    def run_activation(
        self,
        *,
        system_prompt: str,        # role framing ("you are playing one component…")
        user_prompt: str,          # description + trigger + tool reminder
        tools: list[ToolSpec],     # synthesized from wiring; the allowed set
        on_call: ToolDispatch,     # handler invoked per tool call → returns result text
    ) -> ActivationTranscript      # final assistant text + ordered list of calls made
```

- `ToolSpec`: `name`, `description`, and the input field (`narrative: str` raw text now;
  structured slots later — the field schema is the virtual→real hook).
- `on_call(name, args) -> str`: the harness-side router. The provider's only job is to
  faithfully relay each tool call to `on_call` and feed the returned string back to the
  component as the tool result. **The provider holds no domain logic** — it is pure
  transport. This is what lets us swap subprocess-Claude for a direct-API Claude, a
  recorded fixture, or a human at a prompt without touching the harness loop.

### Default: `SubprocessClaudeProvider`

Spawns the `claude` CLI in non-interactive mode and points it at the ad-hoc MCP server.

```
claude -p
  --output-format stream-json   # so we can read tool_use/tool_result events as they stream
  --input-format text
  --mcp-config <ephemeral server config>
  --allowedTools mcp__sim__emit_book_borrowed mcp__sim__query_… mcp__sim__report_finding
  --append-system-prompt "<system_prompt>"
  --model <configurable; default opus>
  "<user_prompt>"
```

Notes that shape the implementation:

- **MCP tool names** surface to Claude as `mcp__<server>__<tool>` (server name `sim`).
  `--allowedTools` is how we enforce rule 2 (tools-from-wiring) at the CLI boundary; the
  handler re-validates server-side as defense in depth and to record the `verdict`.
- **Transport (decision — using stdio):** the MCP server runs as a **stdio server that
  the `claude` child launches** (standard `--mcp-config` stdio entry). To keep the
  handlers in-harness-process and sharing EventStore/SessionLog, the stdio server is a
  tiny sidecar script (`point/sim_mcp.py`) that bridges to the parent harness over a
  unix socket. *Alternative considered:* harness hosts an HTTP/SSE MCP server and the
  child connects by URL — fewer moving parts for shared state, but adds a listening
  socket and an http dependency. **Open for veto** — if you'd rather, we host HTTP and
  drop the sidecar. (Leaning stdio-sidecar to keep it dependency-light and local-only.)
- **Streaming vs. batch:** `--output-format stream-json` lets us log `tool_call`
  entries in real time and matches the session-log topology. The handler return value is
  delivered back through MCP automatically; we don't have to thread it manually.

### Other providers (same interface, later)

- `ManualProvider` — prints the prompt + tool menu to the terminal, reads the human's
  tool choice. Restores the PLAYBOOK's `--manual` contract exactly.
- `RecordedProvider` — replays a fixture transcript for deterministic tests (lets the
  smoke test assert tree topology without a live model).
- `DirectAPIProvider` — Anthropic SDK with real tool-use blocks; no subprocess. For when
  we want speed / no CLI dependency.

Selection: `--provider subprocess|manual|recorded` on the CLI, default `subprocess`.

## The ad-hoc MCP tools

The server exposes the **union of all tools declared anywhere in the feat**, registered
once at startup; each activation *restricts* the usable subset via `--allowedTools`. One
server, per-activation gating — simpler than rebuilding a server each activation.

| Tool | Field(s) | Handler does |
|---|---|---|
| `emit_<event>` | `narrative: str` | wrap via `event_factory`, append to event queue, write `emission` (queued:event), return `"recorded: <event>"` |
| `dispatch_<command>` | `narrative: str` | wrap via `command_factory`, append to command queue, write `emission` (queued:command), return `"queued: <command>"` |
| `query_<name>` | `narrative: str` | run querier sub-activation over the event store, write `query_answer`, return the **answer text inline** |
| `report_finding` | `category: str`, `summary: str`, `detail: str` | write `finding`, mark activation blocked (rule 8), return an ack that tells the component to stop (rule 6/7: no speculative emits) |

Every tool's primary field is **raw text** at level 0 — the component speaks in
narrative, exactly as in the hand-roleplay. The field schema is the single place that
tightens when we go to typed payloads (level 1+).

### What a handler returns matters

The returned string is the component's *only* feedback. So:
- `query_*` returns the actual answer → the component can branch on it (the whole point
  of synchronous sub-activation, rule 10).
- `emit_*`/`dispatch_*` return a terse ack → the component knows it succeeded and can
  continue or finish.
- `report_finding` returns "finding recorded; end your turn without emitting unless the
  outcome is logically deducible" → enforces rules 6–8 in-band.

## Querier sub-activation (jmQ collapse) via the same Provider

`evaluate_query` is **not special** — it is another `Provider.run_activation` with:
- `system_prompt`: "you are a querier; answer ONLY from the event stream below."
- `user_prompt`: query description + args + `event_store.dump()`.
- `tools`: just `report_finding` (the querier's failure mode when the stream can't
  answer). The querier's **final assistant text is the answer**; if it calls
  `report_finding` instead, the query is unanswerable → bubble the finding up.

This keeps one code path for every LLM interaction and makes the provider swap total.

## Open decisions (flag before I build)

1. **Transport**: stdio sidecar (leaning this) vs. harness-hosted HTTP MCP. Affects one
   file (`sim_mcp.py`) and whether we add an http dep.
2. **`report_finding` pause (rule 6)**: in an automated `subprocess` run there's no human
   Director mid-activation. Default: **record + end the activation**, collect for run-end
   resolution (rule 8) — i.e. we honour "a finding ends an activation" but defer the
   ruling. `ManualProvider` keeps the live pause. OK?
3. **First-execution gate (rule 11)**: same issue — auto runs can't pause for Director
   review. Default: **log the gate as a `ruling`-stub entry and proceed**, so the
   topology still shows it; live review only under `ManualProvider`. OK?
4. **Dependencies**: add `mcp` (the Python MCP SDK / FastMCP) via `uv add`. Confirm
   you're fine adding it to the project (or a `point/`-local `uv` script with inline
   deps so it never touches the dizzy package).
