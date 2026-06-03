# Dizzy examples

Worked examples you can read end to end. Each one is committed **already generated
and implemented**, so you can browse the output without running Dizzy.

| Example | What it shows |
|---------|---------------|
| [`guestbook/`](guestbook/) | The minimal feature — one command, procedure, event, projection, model, and query. Wires both Dizzy loops and runs end to end via `demo.py`. |

New to Dizzy? Start with [`guestbook/`](guestbook/) and run:

```bash
uv sync --project examples/guestbook/lib/python-uv
uv run --project examples/guestbook/lib/python-uv python examples/guestbook/demo.py
```
