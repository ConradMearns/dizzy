"""Wire the generated library hold-queue feature together and run it end to end.

This is the glue a host application writes by hand: it owns the database, the
event/command routing, and the wiring. Dizzy generates the typed pieces; this
file connects them.

The point of this example is the POLICY that runs a QUERY to decide which COMMAND
to dispatch:

    BookReturned ─▶ notify_next_on_return ──(query get_next_hold)──▶ NotifyNextPatron

A policy emits commands only — never events. The query informs *which* command it
dispatches (and with what arguments). The host below binds each query into a
closure over the read adapter, so the policy calls it with just the query input,
exactly the way it calls an emitter.

Run inside the workspace environment (from the repo root):

    uv sync --project examples/library/lib/python-uv
    uv run --project examples/library/lib/python-uv python examples/library/demo.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gen_def.pydantic.commands import PlaceHold, ReturnBook, NotifyNextPatron
from gen_def.pydantic.events import HoldPlaced, BookReturned, PatronNotified
from gen_def.pydantic.query.get_next_hold import GetNextHoldInput
from gen_def.sqla.models.holds import Base
from gen_int.python.adapters.sqla import SqlaAdapter
from gen_int.python.procedure.record_hold_context import (
    record_hold_context,
    record_hold_emitters,
)
from gen_int.python.procedure.process_return_context import (
    process_return_context,
    process_return_emitters,
)
from gen_int.python.procedure.send_notification_context import (
    send_notification_context,
    send_notification_emitters,
)
from gen_int.python.projection.hold_store_projection import hold_store_context
from gen_int.python.policy.notify_next_on_return_context import (
    notify_next_on_return_context,
    notify_next_on_return_emitters,
    notify_next_on_return_queries,
)
from gen_int.python.query.get_next_hold import get_next_hold_context

# Each element is its own installed package, exposing a top-level module.
from record_hold import record_hold
from process_return import process_return
from send_notification import send_notification
from hold_store import hold_store
from get_next_hold import get_next_hold
from notify_next_on_return import notify_next_on_return


def main() -> None:
    # The host owns persistence. Here: an in-memory SQLite database.
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    adapter = SqlaAdapter(session=session)

    # --- The query, bound to the read adapter ---
    # The host owns the adapter, so it binds it here. Handlers receive a closure
    # that takes only the query input — symmetric with how they receive emitters.
    def query_get_next_hold(input: GetNextHoldInput):
        return get_next_hold(input, get_next_hold_context(adapter=adapter))

    # --- Event handlers (the host's reaction routing) ---
    # patron_notified is the terminal fact in this demo; the host just reports it.
    def on_patron_notified(event: PatronNotified) -> None:
        print(f"  -> notified {event.patron} that '{event.book_id}' is ready")

    # The notify_next_patron command is dispatched by the policy. The host routes
    # it to its procedure, which emits patron_notified.
    def dispatch_notify_next_patron(command: NotifyNextPatron) -> None:
        send_notification(
            send_notification_context(
                emit=send_notification_emitters(patron_notified=on_patron_notified)
            ),
            command,
        )

    # book_returned triggers the policy. The policy queries the hold queue and,
    # if someone is waiting, dispatches notify_next_patron (routed above).
    def on_book_returned(event: BookReturned) -> None:
        notify_next_on_return(
            event,
            notify_next_on_return_context(
                emit=notify_next_on_return_emitters(
                    notify_next_patron=dispatch_notify_next_patron
                ),
                query=notify_next_on_return_queries(get_next_hold=query_get_next_hold),
            ),
        )

    # hold_placed is folded into the read model by the projection.
    def on_hold_placed(event: HoldPlaced) -> None:
        hold_store(event, hold_store_context(adapter=adapter))

    # --- Procedure contexts (command -> procedure -> event) ---
    record_hold_ctx = record_hold_context(
        emit=record_hold_emitters(hold_placed=on_hold_placed)
    )
    process_return_ctx = process_return_context(
        emit=process_return_emitters(book_returned=on_book_returned)
    )

    # --- Run a scenario ---
    # Two patrons place holds on the same book (Ada first, then Grace).
    print("Holds placed:")
    record_hold(record_hold_ctx, PlaceHold(book_id="dune", patron="Ada"))
    print("  - Ada holds 'dune'")
    record_hold(record_hold_ctx, PlaceHold(book_id="dune", patron="Grace"))
    print("  - Grace holds 'dune'")

    # The book comes back. The policy should consult the queue and notify Ada
    # (the oldest hold) — not Grace.
    print("\nReturning 'dune':")
    process_return(process_return_ctx, ReturnBook(book_id="dune"))

    # A book with no holds: the policy queries, finds nobody, dispatches nothing.
    print("\nReturning 'gardens-of-the-moon' (no holds):")
    process_return(process_return_ctx, ReturnBook(book_id="gardens-of-the-moon"))
    print("  -> no one waiting; nothing dispatched")


if __name__ == "__main__":
    main()
