# Build a guestbook

In this tutorial you build the **guestbook** — the smallest feature that still
exercises both of DIZZY's loops — from an empty directory. By the end of these first
steps you'll have described the feature and generated typed schemas from it.

```
sign_guestbook ─▶ record_signature ─▶ guestbook_signed              (reactivity loop)
guestbook_signed ─▶ signature_store ─▶ guestbook ─▶ list_signatures (data loop)
```

A visitor **signs** the guestbook (a *command*). A *procedure* validates it and emits a
*fact* (an *event*). A *projection* folds that fact into a *model* (a read table). A
*query* reads it back out.

!!! note "Validated tutorial"
    Every command and file on this page is executed and checked by
    `just tutorials-check` (via [byexample](https://byexamples.github.io/byexample/)),
    so it cannot silently drift from the tool. Lines beginning with `$` are commands you
    run; lines beginning with `>` continue the command above (a shell heredoc). Don't
    copy the `$`/`>` markers themselves.

## Before you start

You need DIZZY installed:

```shell
$ dizzy --help | head -n 1
```

Work in a fresh directory. This tutorial's assets — the feature-file, `demo.py`, and the
patches it applies to generated files — ship under the
[tutorial source](https://github.com/PNNL/dizzy/tree/main/docs/tutorials/guestbook);
grab that folder to follow along, or just copy each block by hand as you go:

```shell
$ ls -1
demo.py
edits
guestbook.feat.yaml
```

## Step 1 — Describe the feature

The **feature-file** is the single source of truth: it declares every component of the
domain in one readable artifact. Create `guestbook.feat.yaml` with this content (it also
ships alongside the tutorial, so it's already in your working directory if you grabbed
the folder):

```yaml title="guestbook.feat.yaml"
--8<-- "tutorials/guestbook/guestbook.feat.yaml"
```

That's the whole design. Each entry names a component and, where it matters, how the
components connect (`record_signature` handles `sign_guestbook` and emits
`guestbook_signed`; `signature_store` folds `guestbook_signed` into the `guestbook`
model). Names are `snake_case`; LinkML will compile them to `PascalCase` classes later.

A quick sanity check that the file is in place:

```shell
$ head -n 1 guestbook.feat.yaml
description: Guestbook — visitors sign, signatures are stored and listed
```

## Step 2 — Scaffold the schemas

`dizzy generate definitions` reads the feature-file and writes **LinkML schema stubs**
into `def/`, plus a `libconfig.yaml` that assigns a runtime to each element:

```shell
$ dizzy generate definitions guestbook.feat.yaml .
Generated def/ stubs and libconfig.yaml. Next steps:
<...>
```

Look at what it produced:

```shell
$ ls -1 def
commands.yaml
events.yaml
models
queries
```

The scaffolds are intentionally empty where *you* must decide the shape. Open the
command schema and you'll see its `attributes` left blank for you to fill:

```shell
$ cat def/commands.yaml
id: https://example.org/commands
name: commands
prefixes:
  linkml: https://w3id.org/linkml/
default_range: string
imports:
  - linkml:types
classes:
  sign_guestbook:
    description: A visitor wants to leave a signature
    attributes: {}
```

## Step 3 — Fill in the schema (patching generated files)

This is the heart of the workflow: the generator scaffolds *structure*, and you author
the *field-level detail*. The files **don't start empty** — the scaffold gave each class
everything except the fields, leaving `attributes: {}` for you. A `sign_guestbook`
command needs a visitor name and a message, so edit `def/commands.yaml`:

```diff
--8<-- "tutorials/guestbook/edits/commands.yaml.diff"
```

Each change in this tutorial ships as a patch under `edits/`, so you can apply it
directly (or just make the highlighted edit by hand):

```shell
$ git apply edits/commands.yaml.diff
$ cat def/commands.yaml
id: https://example.org/commands
name: commands
prefixes:
  linkml: https://w3id.org/linkml/
default_range: string
imports:
  - linkml:types
classes:
  sign_guestbook:
    description: A visitor wants to leave a signature
    attributes:
      visitor_name:
        range: string
        required: true
      message:
        range: string
        required: true
```

Do the same for the event. An event is an **immutable fact**, so it must carry
everything needed to replay it — its own id and a timestamp, not just the user-supplied
fields:

```diff
--8<-- "tutorials/guestbook/edits/events.yaml.diff"
```

```shell
$ git apply edits/events.yaml.diff
```

The **model** is the read-optimized table the projection will write into. Its scaffold
starts at `classes: {}`; give it a `Signature` class with an identifier:

```diff
--8<-- "tutorials/guestbook/edits/guestbook.yaml.diff"
```

And the **query** needs the shape of its input and output — here, an optional `limit` in
and a list of formatted lines out:

```diff
--8<-- "tutorials/guestbook/edits/list_signatures.yaml.diff"
```

Apply both:

```shell
$ git apply edits/guestbook.yaml.diff edits/list_signatures.yaml.diff
```

Re-running `dizzy generate definitions` now is safe — it **never clobbers** files you've
edited, so your attributes survive:

```shell
$ dizzy generate definitions guestbook.feat.yaml .
Generated def/ stubs and libconfig.yaml. Next steps:
<...>
$ grep -c 'visitor_name' def/commands.yaml
1
```

Your hand-authored attributes are still there.

## Step 4 — Compile the type packages

`dizzy generate static` runs LinkML over `def/` to produce **`gen_def`** (Pydantic +
SQLAlchemy classes) and **`gen_int`** (typed protocols, contexts, and adapters). Both
land under `lib/python-uv/` as installable packages:

```shell
$ dizzy generate static guestbook.feat.yaml .
<...>
$ ls -1 lib/python-uv
gen_def
gen_int
```

These are generated, not authored — you never edit them. They're the typed contracts the
next step builds against.

## Step 5 — Package each element

`dizzy generate libraries` reads `libconfig.yaml` (every element targets `python-uv` here)
and emits one redistributable package per element, plus the workspace `pyproject.toml`
that ties them and the type packages together:

```shell
$ dizzy generate libraries guestbook.feat.yaml .
<...>
$ ls -1 lib/python-uv
gen_def
gen_int
procedure
projection
pyproject.toml
query
```

Each element package carries a real-signature **implementation stub** in `src/<name>.py`
that raises `NotImplementedError` — the typed shape is there, the logic is yours to write:

```shell
$ cat lib/python-uv/procedure/record_signature/src/record_signature.py
# Implementation stub — fill in your logic here
<...>
    raise NotImplementedError
```

The stub already has the right typed signature — `context` and `command`, both generated
types — and leaves the body to you. You'll see the full original in the next step's diff.

## Step 6 — Implement the stubs

Three elements carry logic: the **procedure** turns a command into an event, the
**projection** folds the event into the model, and the **query** reads it back. Fill them
in — each diff replaces the `NotImplementedError` stub with a real body.

The procedure stamps identity and time (so the event is a self-contained fact) and emits
it:

```diff
--8<-- "tutorials/guestbook/edits/record_signature.py.diff"
```

The projection merges each event into the read model through the SQLAlchemy adapter:

```diff
--8<-- "tutorials/guestbook/edits/signature_store.py.diff"
```

The query reads the model back out, newest first:

```diff
--8<-- "tutorials/guestbook/edits/list_signatures.py.diff"
```

Apply all three:

```shell
$ git apply edits/record_signature.py.diff edits/signature_store.py.diff edits/list_signatures.py.diff
```

## Step 7 — Wire it up and run

Everything DIZZY generates is a typed package; a **host** supplies the glue — the
database, the event routing, and the calls. That's `demo.py`. It owns an in-memory
SQLite database, routes each emitted `guestbook_signed` event into the projection, signs
the guestbook three times, then runs the query:

```python title="demo.py"
--8<-- "tutorials/guestbook/demo.py"
```

Sync the generated workspace and run it:

```shell
$ uv sync --project lib/python-uv
<...>
$ uv run --project lib/python-uv python demo.py
Guestbook (newest first):
  - Edsger: Goto considered harmful
  - Grace: Compiled it
  - Ada: Hello from 1843
```

🎉 **That's the whole feature.** A command flowed through a procedure into an event, a
projection folded it into a model, and a query read it back — both of DIZZY's loops,
generated from a single feature-file and a handful of edits you made to the parts only
you could decide.

Want more? The [`examples/`](https://github.com/PNNL/dizzy/tree/main/examples) directory
has larger worked features — a policy that consults a query, and a multi-step,
policy-driven cascade.
