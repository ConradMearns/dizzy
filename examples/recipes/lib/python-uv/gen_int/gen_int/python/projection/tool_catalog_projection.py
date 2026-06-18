# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import ToolRegistered
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class tool_catalog_context:
    adapter: SqlaAdapter


class tool_catalog_projection(Protocol):
    """Persist each registered tool into the catalog"""

    def __call__(self, event: ToolRegistered, context: tool_catalog_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
