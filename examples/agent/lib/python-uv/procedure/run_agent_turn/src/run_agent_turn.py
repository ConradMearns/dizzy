# Implementation of the run_agent_turn procedure against its generated context.
from datetime import datetime, timezone

import openai

from gen_int.python.procedure.run_agent_turn_context import run_agent_turn_context
from gen_def.pydantic.commands import SendMessage
from gen_def.pydantic.events import UserMessageSent, AgentReplied
from gen_def.pydantic.query.get_conversation import GetConversationInput
from gen_def.pydantic.telemetry import StreamChunk, Usage


def run_agent_turn(
    context: run_agent_turn_context,
    command: SendMessage,
) -> None:
    # 1. Read prior history (scoped to session_id) so the LLM has context.
    history = context.query.get_conversation(
        GetConversationInput(session_id=command.session_id)
    )
    messages = [
        {"role": role, "content": content}
        for role, content in zip(history.roles, history.contents)
    ]
    messages.append({"role": command.role, "content": command.content})

    # 2. Durably record the user's message as a fact.
    context.emit.user_message_sent(
        UserMessageSent(
            session_id=command.session_id,
            content=command.content,
            sent_at=datetime.now(timezone.utc),
        )
    )

    # 3. Stream the reply, forwarding each token chunk to the telemetry sink.
    #    The LLM client config is injected via the environment, not os.environ.
    client = openai.OpenAI(
        api_key=context.env.llm.api_key,
        base_url=context.env.llm.base_url,
    )
    stream = client.chat.completions.create(
        model=context.env.llm.model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
    )

    reply_parts: list[str] = []
    usage = None
    for chunk in stream:
        if chunk.choices:
            delta = chunk.choices[0].delta.content
            if delta:
                reply_parts.append(delta)
                context.telemetry.stream_chunk(StreamChunk(text=delta))
        # The final chunk carries aggregate usage when include_usage is set.
        if getattr(chunk, "usage", None):
            usage = chunk.usage

    # A terminal telemetry chunk carrying usage — transport only, never an event.
    if usage is not None:
        context.telemetry.stream_chunk(
            StreamChunk(
                text="",
                usage=Usage(
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens,
                ),
            )
        )

    # 4. Record the completed reply (with token telemetry) as a durable fact.
    context.emit.agent_replied(
        AgentReplied(
            session_id=command.session_id,
            content="".join(reply_parts),
            replied_at=datetime.now(timezone.utc),
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
            total_tokens=usage.total_tokens if usage else None,
            cost_usd=None,
        )
    )
