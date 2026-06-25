# Dizzy examples

The minimal features — **guestbook**, the **policy that consults a query**, and the
**streaming agent turn** — are now full, validated walkthroughs under
[`docs/tutorials/`](../docs/tutorials/), built end to end and checked by
`just tutorials-check`. Start there.

This directory holds the larger worked feature that doesn't (yet) have a tutorial. It
commits its **feature-file, authored schemas, and element implementations**; the compiled
type packages (`gen_def`/`gen_int`) are generated on demand, so build them before running.

| Example | What it shows |
|---------|---------------|
| [`recipes/`](recipes/) | A **multi-step, policy-driven cascade** over W3C PROV-style events. Three chained recipes (starter ▶ loaf ▶ croutons) where each output feeds the next; batches open *blocked* and a policy advances them as upstream entities are produced. Steps are typed data, not text. Runs via `demo.py` (CLI), a FastAPI server (`server.py`), and a browser UI. |

## Running an example

Generate the type packages, sync the workspace, then run the demo inside it:

```bash
# from the repo root:
dizzy generate static examples/recipes/recipes.feat.yaml examples/recipes
dizzy generate libraries examples/recipes/recipes.feat.yaml examples/recipes
uv sync --project examples/recipes/lib/python-uv
uv run --project examples/recipes/lib/python-uv python examples/recipes/demo.py
```

> Each `demo.py` imports the example's **generated** packages, so it must run inside that
> example's own uv workspace — hence the `--project .../lib/python-uv` flag. A plain
> `uv run demo.py` uses the repo environment and fails with
> `ModuleNotFoundError: No module named 'gen_def'`.
