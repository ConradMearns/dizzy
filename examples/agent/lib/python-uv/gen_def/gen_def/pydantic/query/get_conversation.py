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


linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/queries/get_conversation/',
     'default_range': 'string',
     'description': 'List all messages for a session_id in chronological order, '
                    'including\n'
                    'role, content, timestamps, and assistant token/cost '
                    'telemetry. Used by\n'
                    'the UI to render history and by `run_agent_turn` for LLM '
                    'context.',
     'id': 'https://example.org/queries/get_conversation',
     'imports': ['linkml:types'],
     'name': 'get_conversation',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'examples/agent/def/queries/get_conversation.yaml'} )


class GetConversationInput(ConfiguredBaseModel):
    """
    Input for get_conversation — scopes the read to one conversation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/queries/get_conversation'})

    session_id: str = Field(default=..., description="""Shared conversation key to read.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetConversationInput']} })


class GetConversationOutput(ConfiguredBaseModel):
    """
    Output for get_conversation — messages in order, as parallel lists.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/queries/get_conversation'})

    roles: Optional[list[str]] = Field(default=[], description="""Author per message — \"user\" or \"assistant\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetConversationOutput']} })
    contents: Optional[list[str]] = Field(default=[], description="""Message text per row.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetConversationOutput']} })
    created_ats: Optional[list[datetime ]] = Field(default=[], description="""Timestamp per row; the chronological ordering key.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetConversationOutput']} })
    total_tokens: Optional[list[int]] = Field(default=[], description="""Token usage per row; empty/zero for user rows.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetConversationOutput']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
GetConversationInput.model_rebuild()
GetConversationOutput.model_rebuild()
