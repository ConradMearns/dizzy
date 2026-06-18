# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import StepInputAdded
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class step_input_catalog_context:
    adapter: SqlaAdapter


class step_input_catalog_projection(Protocol):
    """Persist each step input into the catalog"""

    def __call__(self, event: StepInputAdded, context: step_input_catalog_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
