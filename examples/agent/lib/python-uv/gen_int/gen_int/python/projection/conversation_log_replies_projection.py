# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import AgentReplied
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class conversation_log_replies_context:
    adapter: SqlaAdapter


class conversation_log_replies_projection(Protocol):
    """Fold `agent_replied` rows (with telemetry) into the conversations model."""

    def __call__(self, event: AgentReplied, context: conversation_log_replies_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
