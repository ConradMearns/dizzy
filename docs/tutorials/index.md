# Tutorials

Learning-oriented lessons that take you through DIZZY hands-on.

- **[Build a guestbook](guestbook.md)** — take a feature from an empty directory all the
  way to a running demo: describe it, generate and fill in typed schemas, package each
  element, implement the stubs, and watch the signatures print back out. Every command,
  edit, and output is executed and checked by `just tutorials-check`.
- **[A policy that consults a query](library.md)** — build a library hold queue whose
  centerpiece is a policy that runs a query to decide which command to dispatch.

See also:

- `dizzy onboard` — the agent-facing orientation.
- [`examples/`](https://github.com/PNNL/dizzy/tree/main/examples) — larger worked features
  (a policy consulting a query; a multi-step policy-driven cascade).
