# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import UserMessageSent
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class conversation_log_context:
    adapter: SqlaAdapter


class conversation_log_projection(Protocol):
    """Fold `user_message_sent` and `agent_replied` into the conversations
model as ordered message rows, preserving role, content, timestamps,
and (for assistant rows) token/cost telemetry."""

    def __call__(self, event: UserMessageSent, context: conversation_log_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
