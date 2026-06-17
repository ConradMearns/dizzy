# Dizzy examples

Worked examples you can read end to end. Each one is committed **already generated
and implemented**, so you can browse the output without running Dizzy.

| Example | What it shows |
|---------|---------------|
| [`guestbook/`](guestbook/) | The minimal feature — one command, procedure, event, projection, model, and query. Wires both Dizzy loops and runs end to end via `demo.py`. |
| [`library/`](library/) | A **policy that runs a query** to decide which command to dispatch. When a book is returned, the policy consults the hold queue and notifies the next patron in line. Runs end to end via `demo.py`. |

New to Dizzy? Start with [`guestbook/`](guestbook/) and run:

```bash
uv sync --project examples/guestbook/lib/python-uv
uv run --project examples/guestbook/lib/python-uv python examples/guestbook/demo.py
```

Then see a policy consult a query in [`library/`](library/):

```bash
uv sync --project examples/library/lib/python-uv
uv run --project examples/library/lib/python-uv python examples/library/demo.py
```

> Each `demo.py` imports the example's **generated** packages, so it must run inside
> that example's own uv workspace — hence the `--project .../lib/python-uv` flag.
> A plain `uv run demo.py` uses the repo environment and fails with
> `ModuleNotFoundError: No module named 'gen_def'`.
