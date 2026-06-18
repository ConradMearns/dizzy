# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.find_blocked_batches import FindBlockedBatchesInput, FindBlockedBatchesOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class find_blocked_batches_context:
    adapter: SqlaAdapter


class find_blocked_batches_query(Protocol):
    """The ids of batches blocked waiting for a given entity type"""

    def __call__(
        self, input: FindBlockedBatchesInput, context: find_blocked_batches_context
    ) -> FindBlockedBatchesOutput:
        ...
