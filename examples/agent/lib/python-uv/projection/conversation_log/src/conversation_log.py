# Implementation stub — fill in your logic here
from gen_int.python.projection.conversation_log_projection import conversation_log_projection
from gen_int.python.projection.conversation_log_projection import conversation_log_context
from gen_def.pydantic.events import UserMessageSent


def conversation_log(
    event: UserMessageSent,
    context: conversation_log_context,
) -> None:
    raise NotImplementedError
