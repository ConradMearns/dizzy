# A batch's recipe_id, requires_type, and status.
from gen_int.python.query.get_batch import get_batch_context
from gen_def.pydantic.query.get_batch import GetBatchInput, GetBatchOutput
from gen_def.sqla.models.batches import Batch


def get_batch(input: GetBatchInput, context: get_batch_context) -> GetBatchOutput:
    batch = context.adapter.session.get(Batch, input.batch_id)
    if batch is None:
        return GetBatchOutput()
    return GetBatchOutput(
        recipe_id=batch.recipe_id,
        requires_type=batch.requires_type,
        status=batch.status,
    )
