# The ids of batches blocked waiting for a given entity type, oldest-opened first
# (the FIFO order in which they should be unblocked as lots become available).
from gen_int.python.query.find_blocked_batches import find_blocked_batches_context
from gen_def.pydantic.query.find_blocked_batches import (
    FindBlockedBatchesInput,
    FindBlockedBatchesOutput,
)
from gen_def.sqla.models.batches import Batch


def find_blocked_batches(
    input: FindBlockedBatchesInput, context: find_blocked_batches_context
) -> FindBlockedBatchesOutput:
    rows = (
        context.adapter.session.query(Batch)
        .filter(
            Batch.status == "blocked",
            Batch.requires_type == input.entity_type,
        )
        .order_by(Batch.opened_at, Batch.id)
        .all()
    )
    return FindBlockedBatchesOutput(batch_ids=[r.id for r in rows])
