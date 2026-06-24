# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import SendMessage
from gen_int.python.procedure.run_agent_turn_context import (
    run_agent_turn_context,
)


class run_agent_turn_protocol(Protocol):
    """Handle a user message by producing an agent reply.

1. Emit `user_message_sent` to durably record the user's message.
2. Call the LLM with stream=True, forwarding each token chunk to the
   `stream_chunk` telemetry sink.
3. On stream completion, report aggregate token usage via the `usage`
   telemetry sink, then emit `agent_replied` with the full reply text.

```mermaid
flowchart TD
  cmd[send_message] --> umsg[user_message_sent]
  umsg --> llm[LLM stream]
  llm -- chunks --> stream[stream_chunk]
  llm -- done --> usage[usage]
  usage --> reply[agent_replied]
```"""

    def __call__(
        self,
        context: run_agent_turn_context,
        command: SendMessage,
    ) -> None:
        ...
