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
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




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


linkml_meta = LinkMLMeta({'default_prefix': 'dedupe',
     'default_range': 'string',
     'description': 'LinkML schema for mutation objects that define inputs and '
                    'outputs for storing events in the event sourcing system.',
     'id': 'https://example.org/dedupe/mutations',
     'imports': ['linkml:types', 'events'],
     'name': 'dedupe-mutations-schema',
     'prefixes': {'dedupe': {'prefix_prefix': 'dedupe',
                             'prefix_reference': 'https://example.org/dedupe/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'def/mutations.yaml',
     'title': 'Dedupe Mutations Data Model'} )


class DomainEvent(ConfiguredBaseModel):
    """
    Base class for all domain events - immutable facts about what happened
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dedupe/events'})

    pass


class TestMessage(DomainEvent):
    """
    Simple test event with a single message string
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/events'})

    message: str = Field(default=..., description="""The test message content""", json_schema_extra = { "linkml_meta": {'alias': 'message', 'domain_of': ['TestMessage']} })


class FileItemScanned(DomainEvent):
    """
    Event recording that a file item was scanned
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/events'})

    partition_uuid: str = Field(default=..., description="""UUID of the partition containing this file""", json_schema_extra = { "linkml_meta": {'alias': 'partition_uuid', 'domain_of': ['FileItemScanned']} })
    path: str = Field(default=..., description="""Full path to the file within the partition""", json_schema_extra = { "linkml_meta": {'alias': 'path', 'domain_of': ['FileItemScanned']} })
    size: int = Field(default=..., description="""Size of the file in bytes""", json_schema_extra = { "linkml_meta": {'alias': 'size', 'domain_of': ['FileItemScanned']} })
    content_hash: str = Field(default=..., description="""Hash of the file contents""", json_schema_extra = { "linkml_meta": {'alias': 'content_hash', 'domain_of': ['FileItemScanned']} })


class MutationInput(ConfiguredBaseModel):
    """
    Base class for all mutation input parameter objects
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dedupe/mutations'})

    pass


class Mutation(ConfiguredBaseModel):
    """
    Base class for all mutation result objects
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dedupe/mutations'})

    pass


class EventRecordInput(MutationInput):
    """
    Input parameters for storing an event record
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/mutations'})

    event: DomainEvent = Field(default=..., description="""The domain event to store""", json_schema_extra = { "linkml_meta": {'alias': 'event', 'domain_of': ['EventRecordInput', 'EventRecord']} })


class EventRecord(Mutation):
    """
    Result of storing an event record
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/mutations'})

    event_hash: str = Field(default=..., description="""SHA256 hash of the event (content-addressable primary key)""", json_schema_extra = { "linkml_meta": {'alias': 'event_hash', 'domain_of': ['EventRecord']} })
    event_type: str = Field(default=..., description="""Class name of the event (e.g., \"TestMessage\", \"FileItemScanned\")""", json_schema_extra = { "linkml_meta": {'alias': 'event_type', 'domain_of': ['EventRecord']} })
    event: DomainEvent = Field(default=..., description="""The original event that was stored""", json_schema_extra = { "linkml_meta": {'alias': 'event', 'domain_of': ['EventRecordInput', 'EventRecord']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
DomainEvent.model_rebuild()
TestMessage.model_rebuild()
FileItemScanned.model_rebuild()
MutationInput.model_rebuild()
Mutation.model_rebuild()
EventRecordInput.model_rebuild()
EventRecord.model_rebuild()

