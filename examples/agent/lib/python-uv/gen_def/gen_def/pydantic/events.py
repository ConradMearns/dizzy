from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )

    @model_serializer(mode='wrap', when_used='unless-none')
    def treat_empty_lists_as_none(
            self, handler: SerializerFunctionWrapHandler,
            info: SerializationInfo) -> dict[str, Any]:
        if info.exclude_none:
            _instance = self.model_copy()
            for field, field_info in type(_instance).model_fields.items():
                if getattr(_instance, field) == [] and not(
                        field_info.is_required()):
                    setattr(_instance, field, None)
        else:
            _instance = self
        return handler(_instance, info)



class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/events/',
     'default_range': 'string',
     'id': 'https://example.org/events',
     'imports': ['linkml:types'],
     'name': 'events',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'examples/agent/def/events.yaml'} )


class UserMessageSent(ConfiguredBaseModel):
    """
    A user message was appended to a conversation.
    Carries session_id, content, and sent_at.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    session_id: str = Field(default=..., description="""Shared conversation key this message belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['user_message_sent', 'agent_replied']} })
    content: str = Field(default=..., description="""The user's message text.""", json_schema_extra = { "linkml_meta": {'domain_of': ['user_message_sent', 'agent_replied']} })
    sent_at: datetime  = Field(default=..., description="""When the user message was recorded.""", json_schema_extra = { "linkml_meta": {'domain_of': ['user_message_sent']} })


class AgentReplied(ConfiguredBaseModel):
    """
    The agent completed a reply in a conversation.
    Carries session_id, content, replied_at, and token/cost telemetry
    (prompt_tokens, completion_tokens, total_tokens, cost_usd). Telemetry is
    observed provenance from the model provider, not a derivation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    session_id: str = Field(default=..., description="""Shared conversation key this reply belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['user_message_sent', 'agent_replied']} })
    content: str = Field(default=..., description="""The agent's full reply text.""", json_schema_extra = { "linkml_meta": {'domain_of': ['user_message_sent', 'agent_replied']} })
    replied_at: datetime  = Field(default=..., description="""When the agent reply was recorded.""", json_schema_extra = { "linkml_meta": {'domain_of': ['agent_replied']} })
    prompt_tokens: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['agent_replied']} })
    completion_tokens: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['agent_replied']} })
    total_tokens: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['agent_replied']} })
    cost_usd: Optional[float] = Field(default=None, description="""Provider-reported cost of the turn, in USD.""", json_schema_extra = { "linkml_meta": {'domain_of': ['agent_replied']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
UserMessageSent.model_rebuild()
AgentReplied.model_rebuild()
