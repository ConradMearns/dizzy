# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.list_batches import ListBatchesInput, ListBatchesOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class list_batches_context:
    adapter: SqlaAdapter


class list_batches_query(Protocol):
    """All batches with their status, for a dashboard"""

    def __call__(
        self, input: ListBatchesInput, context: list_batches_context
    ) -> ListBatchesOutput:
        ...
