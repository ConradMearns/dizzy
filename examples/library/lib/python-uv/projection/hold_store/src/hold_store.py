# Implementation — fold each HoldPlaced event into the holds read model.
from uuid import uuid4

from gen_int.python.projection.hold_store_projection import hold_store_context
from gen_def.pydantic.events import HoldPlaced
from gen_def.sqla.models.holds import Hold


def hold_store(
    event: HoldPlaced,
    context: hold_store_context,
) -> None:
    # context.adapter is a SqlaAdapter — it hands us a live SQLAlchemy session.
    # Each placed hold becomes a row; get_next_hold reads these back, ordered by
    # placed_at, to find who is first in line.
    context.adapter.session.add(
        Hold(
            id=str(uuid4()),
            book_id=event.book_id,
            patron=event.patron,
            placed_at=event.placed_at,
        )
    )
    context.adapter.session.commit()
