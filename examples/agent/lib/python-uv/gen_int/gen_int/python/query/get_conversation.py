# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.get_conversation import GetConversationInput, GetConversationOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class get_conversation_context:
    adapter: SqlaAdapter


class get_conversation_query(Protocol):
    """List all messages for a `session_id` in chronological order, including
role, content, timestamps, and assistant token/cost telemetry. Used by
the UI to render history and by `run_agent_turn` for LLM context.
"""

    def __call__(
        self, input: GetConversationInput, context: get_conversation_context
    ) -> GetConversationOutput:
        ...
