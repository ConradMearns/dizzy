# When an entity is produced, any batch that was blocked waiting for that entity
# type is now ready. Consult find_blocked_batches and dispatch advance_batch for
# each — the host routes advance_batch into run_batch, whose entity_produced
# re-triggers this policy. The cascade ends when no batch is waiting.
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
    for batch_id in waiting.batch_ids:
        context.emit.advance_batch(AdvanceBatch(batch_id=batch_id))
