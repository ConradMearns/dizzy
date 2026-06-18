# All batches with their status, as parallel lists (one entry per batch).
from gen_int.python.query.list_batches import list_batches_context
from gen_def.pydantic.query.list_batches import ListBatchesInput, ListBatchesOutput
from gen_def.sqla.models.batches import Batch


def list_batches(input: ListBatchesInput, context: list_batches_context) -> ListBatchesOutput:
    rows = context.adapter.session.query(Batch).order_by(Batch.id).all()
    return ListBatchesOutput(
        batch_ids=[r.id for r in rows],
        recipe_ids=[r.recipe_id for r in rows],
        requires_types=[r.requires_type or "" for r in rows],
        statuses=[r.status for r in rows],
    )
