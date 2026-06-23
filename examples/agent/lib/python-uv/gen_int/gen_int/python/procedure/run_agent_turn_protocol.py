# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import SendMessage
from gen_int.python.procedure.run_agent_turn_context import (
    run_agent_turn_context,
)


class run_agent_turn_protocol(Protocol):
    """Handle a user message by producing an agent reply.

1. Read prior conversation history via `get_conversation` so the LLM has
   context.
2. Emit `user_message_sent` to durably record the user's message.
3. Call the LLM with stream=True, forwarding each token chunk to the
   caller-supplied telemetry sink.
4. On stream completion, emit `agent_replied` carrying the full reply
   text and the aggregate token/cost usage returned by the provider.

```mermaid
flowchart TD
  cmd[send_message] --> hist[get_conversation]
  hist --> umsg[user_message_sent]
  umsg --> llm[LLM stream]
  llm -- chunks --> telemetry[Chunk Stream]
  llm -- done --> reply[agent_replied + usage]
```"""

    def __call__(
        self,
        context: run_agent_turn_context,
        command: SendMessage,
    ) -> None:
        ...
