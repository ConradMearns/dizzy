# Implementation — read the holds model for the next patron waiting on a book.
from gen_int.python.query.get_next_hold import get_next_hold_context
from gen_def.pydantic.query.get_next_hold import GetNextHoldInput, GetNextHoldOutput
from gen_def.sqla.models.holds import Hold


def get_next_hold(
    input: GetNextHoldInput,
    context: get_next_hold_context,
) -> GetNextHoldOutput:
    # The oldest hold for this book is first in line (FIFO by placed_at).
    row = (
        context.adapter.session.query(Hold)
        .filter(Hold.book_id == input.book_id)
        .order_by(Hold.placed_at.asc())
        .first()
    )
    # When the queue is empty, patron is None — the policy reads that as
    # "no one waiting" and dispatches nothing.
    return GetNextHoldOutput(patron=row.patron if row is not None else None)
