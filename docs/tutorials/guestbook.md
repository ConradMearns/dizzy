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

Work in a fresh directory. The file edits in Step 3 ship as patches under `edits/` so
you can apply them directly — grab that folder from the
[tutorial source](https://github.com/PNNL/dizzy/tree/main/docs/tutorials/guestbook), or
just make the highlighted changes by hand as you go:

```shell
$ ls -1 edits
commands.yaml.diff
events.yaml.diff
```

## Step 1 — Describe the feature

The **feature-file** is the single source of truth: it declares every component of the
domain in one readable artifact. Create `guestbook.feat.yaml`:

```shell
$ cat > guestbook.feat.yaml <<'YAML'
> description: Guestbook — visitors sign, signatures are stored and listed
>
> commands:
>   sign_guestbook: A visitor wants to leave a signature
>
> events:
>   guestbook_signed: A visitor signed the guestbook
>
> procedures:
>   record_signature:
>     description: Validate the signature and record it as a fact
>     command: sign_guestbook
>     emits:
>       - guestbook_signed
>
> models:
>   guestbook:
>     description: Stored guestbook signatures
>     adapters:
>       - sqla
>
> projections:
>   signature_store:
>     description: Persist each signature into the guestbook model
>     event: guestbook_signed
>     model: guestbook
>     adapter: sqla
>
> queries:
>   list_signatures:
>     description: List all guestbook signatures, newest first
>     model: guestbook
>     adapter: sqla
> YAML
```

That's the whole design. Each entry names a component and, where it matters, how the
components connect (`record_signature` handles `sign_guestbook` and emits
`guestbook_signed`; `signature_store` folds `guestbook_signed` into the `guestbook`
model). Names are `snake_case`; LinkML will compile them to `PascalCase` classes later.

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

Re-running `dizzy generate definitions` now is safe — it **never clobbers** files you've
edited, so your attributes survive:

```shell
$ dizzy generate definitions guestbook.feat.yaml .
Generated def/ stubs and libconfig.yaml. Next steps:
<...>
$ grep -c 'visitor_name' def/commands.yaml
1
```

Your hand-authored attribute is still there.

## Where this is going

You've described the feature and given its commands and events a concrete shape. Next
(in the steps to come) you'll compile these schemas into typed packages with
`dizzy generate static`, split each element into a runtime package with
`dizzy generate libraries`, implement the three generated stubs, and run a demo that
lists the signatures back out.

For the finished, fully-implemented version of everything above, see
[`examples/guestbook`](https://github.com/PNNL/dizzy/tree/main/examples/guestbook).
