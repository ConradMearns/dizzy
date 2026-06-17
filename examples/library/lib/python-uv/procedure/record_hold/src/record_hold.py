# Implementation — turn a PlaceHold command into a HoldPlaced fact.
from datetime import datetime, timezone

from gen_int.python.procedure.record_hold_context import record_hold_context
from gen_def.pydantic.commands import PlaceHold
from gen_def.pydantic.events import HoldPlaced


def record_hold(
    context: record_hold_context,
    command: PlaceHold,
) -> None:
    # Business rule: a hold needs both a book and a patron.
    if not command.book_id.strip() or not command.patron.strip():
        raise ValueError("a hold requires both book_id and patron")

    # Stamp time at emit time — the event is the immutable record of the hold,
    # and placed_at is what get_next_hold later orders the queue by.
    context.emit.hold_placed(
        HoldPlaced(
            book_id=command.book_id.strip(),
            patron=command.patron.strip(),
            placed_at=datetime.now(timezone.utc),
        )
    )
