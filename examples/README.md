# Dizzy examples

Worked examples you can read end to end. Each commits its **feature-file, authored
schemas, and element implementations**; the compiled type packages (`gen_def`/`gen_int`)
are generated on demand, so build them before running a demo (see below).

| Example | What it shows | Tutorial |
|---------|---------------|----------|
| [`library/`](library/) | A **policy that runs a query** to decide which command to dispatch. When a book is returned, the policy consults the hold queue and notifies the next patron in line. Runs end to end via `demo.py`. | [A policy that consults a query](../docs/tutorials/library.md) |
| [`agent/`](agent/) | A **streaming LLM agent turn** using **environment** (injected config) and **telemetry** (observation sinks). Streams a reply token by token, then records the completed reply as a durable event. | [A streaming agent turn](../docs/tutorials/agent.md) |
| [`recipes/`](recipes/) | A **multi-step, policy-driven cascade** over W3C PROV-style events. Three chained recipes (starter ▶ loaf ▶ croutons) where each output feeds the next; batches open *blocked* and a policy advances them as upstream entities are produced. Steps are typed data, not text. Runs via `demo.py` (CLI), a FastAPI server (`server.py`), and a browser UI. | — |

> **New to Dizzy?** Start with the
> [Build a guestbook tutorial](../docs/tutorials/guestbook.md) — it builds the minimal
> feature from scratch, end to end, with every step validated. Each tutorial above is
> likewise executed and checked by `just tutorials-check`.

## Running an example

Generate the type packages, sync the workspace, then run the demo inside it:

```bash
# from the repo root, for the library example:
dizzy generate static examples/library/library.feat.yaml examples/library
dizzy generate libraries examples/library/library.feat.yaml examples/library
uv sync --project examples/library/lib/python-uv
uv run --project examples/library/lib/python-uv python examples/library/demo.py
```

> Each `demo.py` imports the example's **generated** packages, so it must run inside that
> example's own uv workspace — hence the `--project .../lib/python-uv` flag. A plain
> `uv run demo.py` uses the repo environment and fails with
> `ModuleNotFoundError: No module named 'gen_def'`.
