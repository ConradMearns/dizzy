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


linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/models/conversations/',
     'default_range': 'string',
     'description': 'Append-only log of messages (user + assistant) per '
                    'conversation, with\n'
                    'per-reply token/cost telemetry. Rebuilt from events by the '
                    'projection.\n'
                    '\n'
                    'Every row relies on a shared session_id — the conversation '
                    'key. A\n'
                    'conversation is exactly the set of rows sharing one '
                    'session_id, ordered\n'
                    'by created_at.',
     'id': 'https://example.org/models/conversations',
     'imports': ['linkml:types'],
     'name': 'conversations',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'examples/agent/def/models/conversations.yaml'} )


class Message(ConfiguredBaseModel):
    """
    One message row in a conversation, keyed by session_id.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/models/conversations'})

    id: str = Field(default=..., description="""Surrogate row id (unique per message).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })
    session_id: str = Field(default=..., description="""Shared conversation key this row belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })
    role: str = Field(default=..., description="""Author of the message — \"user\" or \"assistant\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })
    content: str = Field(default=..., description="""The message text.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })
    created_at: datetime  = Field(default=..., description="""Ordering key within a conversation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })
    prompt_tokens: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })
    completion_tokens: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })
    total_tokens: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })
    cost_usd: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Message']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Message.model_rebuild()
