# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import UserMessageSent
from gen_def.pydantic.events import AgentReplied
from gen_def.pydantic.query.get_conversation import GetConversationInput, GetConversationOutput
from gen_def.pydantic.environment import Llm
from gen_def.pydantic.telemetry import StreamChunk


@dataclass
class run_agent_turn_emitters:
    user_message_sent: Callable[[UserMessageSent], None]
    agent_replied: Callable[[AgentReplied], None]


@dataclass
class run_agent_turn_queries:
    get_conversation: Callable[[GetConversationInput], GetConversationOutput]


@dataclass
class run_agent_turn_env:
    llm: Llm


@dataclass
class run_agent_turn_telemetry:
    stream_chunk: Callable[[StreamChunk], None]


@dataclass
class run_agent_turn_context:
    emit: run_agent_turn_emitters
    query: run_agent_turn_queries
    env: run_agent_turn_env
    telemetry: run_agent_turn_telemetry
