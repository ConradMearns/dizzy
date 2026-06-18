# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import BatchCompleted
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class batch_finalizer_context:
    adapter: SqlaAdapter


class batch_finalizer_projection(Protocol):
    """Mark a batch completed when it finishes running"""

    def __call__(self, event: BatchCompleted, context: batch_finalizer_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
