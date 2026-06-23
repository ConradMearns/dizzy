# Implementation stub — fill in your logic here
from gen_int.python.projection.conversation_log_replies_projection import conversation_log_replies_projection
from gen_int.python.projection.conversation_log_replies_projection import conversation_log_replies_context
from gen_def.pydantic.events import AgentReplied


def conversation_log_replies(
    event: AgentReplied,
    context: conversation_log_replies_context,
) -> None:
    raise NotImplementedError
