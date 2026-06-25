# DIZZY

DIZZY is a methodology and code generator for event-sourced software. A business domain
is expressed in a single artifact — the **feature-file** — that is both literate design
and the source of a checkable implementation. From it, DIZZY generates typed contracts,
deployment, stubs, and tests as redistributable libraries across multiple runtimes.

Two loops define the model:

```
Commands → Procedures → Events → Policies  → Commands   (reactivity loop)
Events   → Projections → Models → Queries  → Procedures (data loop)
```

## Documentation

This site is organized along the [Diátaxis](https://diataxis.fr/) framework:

- **[Tutorials](tutorials/index.md)** — learning-oriented lessons for getting started.
- **[How-to guides](how-to/index.md)** — task-oriented recipes for specific goals.
- **[Reference](reference/SPECIFICATION.md)** — the feature-file format spec and the
  generated [code API](reference/api/index.md) reference.
- **[Explanation](explanation/simulate-playbook.md)** — background, design records, and
  the whitepaper.

> The CLI's own documentation ships with the tool: run `dizzy docs`, `dizzy docs authoring`,
> and `dizzy onboard`.
