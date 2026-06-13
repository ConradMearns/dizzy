# Library hold queue — a policy that queries

The smallest feature that shows a **policy consulting a query to decide which
command to dispatch**:

```
PlaceHold  ─▶ record_hold      ─▶ HoldPlaced                              (reactivity)
HoldPlaced ─▶ hold_store       ─▶ holds ─▶ get_next_hold                  (data)

ReturnBook ─▶ process_return   ─▶ BookReturned                           (reactivity)
BookReturned ─▶ notify_next_on_return ──(query get_next_hold)──▶ NotifyNextPatron
NotifyNextPatron ─▶ send_notification ─▶ PatronNotified
```

A patron places a **hold** on a checked-out book (a command). A **procedure** records
it as a **fact**, and a **projection** folds that fact into the `holds` **model** — the
queue. When the book is **returned**, the `book_returned` fact triggers the
**policy** `notify_next_on_return`. The policy runs the **query** `get_next_hold` to
find who is first in line and — only if someone is waiting — **dispatches** the
`notify_next_patron` command.

## Why this example exists

Policies are the reactivity loop's decision point, but a policy often can't decide what
to do from the triggering event alone — it needs to look at read state. This is what
`policies.queries` is for:

- **A policy emits commands only — never events.** To change state, it dispatches a
  command, which flows through the normal `command → procedure → event` chain
  (`notify_next_patron → send_notification → patron_notified`).
- **A query informs *which* command** the policy dispatches, and with what arguments.
  Here, `get_next_hold` decides *whether* anyone is notified and *who*.

Contrast with a **procedure**, which handles a command and may also query — but a
procedure emits events directly. The query role is the same in both; the emit target
differs (procedures → events, policies → commands).

## The feature file

[`library.feat.yaml`](library.feat.yaml) declares the policy with both `queries` and
`emits`:

```yaml
policies:
  notify_next_on_return:
    description: >-
      When a book is returned, consult the hold queue and, if a patron is
      waiting, dispatch a notification command for the next one in line.
    event: book_returned
    queries:
      - get_next_hold
    emits:
      - notify_next_patron
```

That `queries` list is the whole point: Dizzy injects a typed `query` field into the
policy's generated context, alongside the usual `emit` field. The policy implementation
([`lib/python-uv/policy/notify_next_on_return/src/notify_next_on_return.py`](lib/python-uv/policy/notify_next_on_return/src/notify_next_on_return.py))
calls `context.query.get_next_hold(...)` and dispatches a command only if someone is
waiting.

> **Host-bound queries.** A query needs the read adapter, which the *host* owns — so
> the host binds it. The generated `query` field is a `Callable[[Input], Output]`
> closure (symmetric with `emit`), and the handler calls it with just the query input.
> See how [`demo.py`](demo.py) binds `get_next_hold` over the SQLite adapter.

## Run it

The generated `lib/python-uv/` is a uv workspace. Sync it once, then run `demo.py`
inside that environment — from the repository root:

```bash
uv sync --project examples/library/lib/python-uv
uv run --project examples/library/lib/python-uv python examples/library/demo.py
```

Expected output:

```
Holds placed:
  - Ada holds 'dune'
  - Grace holds 'dune'

Returning 'dune':
  -> notified Ada that 'dune' is ready

Returning 'gardens-of-the-moon' (no holds):
  -> no one waiting; nothing dispatched
```

Ada placed her hold first, so when `dune` comes back she is notified — not Grace. A
book with no holds returns an empty queue, and the policy dispatches nothing. The
decision lives in read state, which is exactly why the policy needs the query.

## Rebuild it from scratch

`def/` stubs and the `src/` implementations inside `lib/` are **never overwritten**, so
to regenerate them too, remove them.

```bash
# from the repo root
rm -rf examples/library/lib

# 1. scaffold def/ LinkML schemas + libconfig.yaml (idempotent; won't clobber edits)
uv run dizzy generate definitions examples/library/library.feat.yaml examples/library

# 2. (human step) fill in attributes in def/*.yaml — see the committed files here

# 3. compile LinkML into the gen_def/gen_int type packages under lib/python-uv/
uv run dizzy generate static examples/library/library.feat.yaml examples/library

# 4. split each element into a redistributable runtime package
uv run dizzy generate libraries examples/library/library.feat.yaml examples/library

# 5. (human step) implement the src/ stubs in lib/python-uv/<kind>/<name>/src/
#    — see the committed files here, especially policy/notify_next_on_return/
```

For the full three-stage workflow and the layout of what gets generated, see
[`guestbook/`](../guestbook/) and `dizzy docs authoring`.
