# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.get_batch import GetBatchInput, GetBatchOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class get_batch_context:
    adapter: SqlaAdapter


class get_batch_query(Protocol):
    """A batch's recipe_id, requires_type, and status"""

    def __call__(
        self, input: GetBatchInput, context: get_batch_context
    ) -> GetBatchOutput:
        ...
