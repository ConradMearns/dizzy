"""Wire the generated guestbook feature together and run it end to end.

This is the glue a host application writes by hand: it owns the database, the
event log, and the wiring. Dizzy generates the typed pieces (commands, events,
contexts, adapters, model tables) and the per-element packages under
`lib/python-uv/`; this file just connects them.

Everything imported here is an installed workspace package, so run demo inside
the workspace environment (from the repo root):

    uv sync --project examples/guestbook/lib/python-uv
    uv run --project examples/guestbook/lib/python-uv python examples/guestbook/demo.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gen_def.pydantic.commands import SignGuestbook
from gen_def.pydantic.events import GuestbookSigned
from gen_def.pydantic.query.list_signatures import ListSignaturesInput
from gen_def.sqla.models.guestbook import Base
from gen_int.python.adapters.sqla import SqlaAdapter
from gen_int.python.procedure.record_signature_context import (
    record_signature_context,
    record_signature_emitters,
)
from gen_int.python.projection.signature_store_projection import signature_store_context
from gen_int.python.query.list_signatures import list_signatures_context

# Each element is its own installed package, exposing a top-level module.
from record_signature import record_signature
from signature_store import signature_store
from list_signatures import list_signatures


def main() -> None:
    # The host owns persistence. Here: an in-memory SQLite database.
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    adapter = SqlaAdapter(session=session)

    # --- Reactivity loop: command -> procedure -> event -> projection ---
    # The procedure emits events; the host routes each emitted event into the
    # projections that listen for it. Here we route guestbook_signed straight
    # into signature_store.
    def on_guestbook_signed(event: GuestbookSigned) -> None:
        signature_store(event, signature_store_context(adapter=adapter))

    proc_context = record_signature_context(
        emit=record_signature_emitters(guestbook_signed=on_guestbook_signed)
    )

    for name, message in [
        ("Ada", "Hello from 1843"),
        ("Grace", "Compiled it"),
        ("Edsger", "Goto considered harmful"),
    ]:
        record_signature(proc_context, SignGuestbook(visitor_name=name, message=message))

    # --- Data loop: query reads the model the projection built ---
    result = list_signatures(
        ListSignaturesInput(limit=10),
        list_signatures_context(adapter=adapter),
    )

    print("Guestbook (newest first):")
    for line in result.signatures:
        print(f"  - {line}")


if __name__ == "__main__":
    main()
