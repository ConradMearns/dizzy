# When an entity is produced, exactly one lot of it now exists — so it can unblock
# exactly one waiting batch. Consult find_blocked_batches (oldest-first) and dispatch
# advance_batch for only the first. The host routes advance_batch into run_batch,
# whose own entity_produced re-triggers this policy, so producing N lots advances N
# waiting batches one-per-lot; the cascade ends when nothing is waiting.
from gen_int.python.policy.advance_ready_batches_context import advance_ready_batches_context
from gen_def.pydantic.events import EntityProduced
from gen_def.pydantic.commands import AdvanceBatch
from gen_def.pydantic.query.find_blocked_batches import FindBlockedBatchesInput


def advance_ready_batches(
    event: EntityProduced,
    context: advance_ready_batches_context,
) -> None:
    waiting = context.query.find_blocked_batches(
        FindBlockedBatchesInput(entity_type=event.entity_type)
    )
    if waiting.batch_ids:
        context.emit.advance_batch(AdvanceBatch(batch_id=waiting.batch_ids[0]))
