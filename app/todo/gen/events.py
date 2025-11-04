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


linkml_meta = LinkMLMeta({'default_prefix': 'todo',
     'default_range': 'string',
     'description': 'LinkML schema for domain events that capture immutable facts '
                    'about what has happened in the system.',
     'id': 'https://example.org/todo/events',
     'imports': ['linkml:types',
                 '../../../pkg/dizzy/src/dizzy/def/events',
                 'models'],
     'name': 'todo-events-schema',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'todo': {'prefix_prefix': 'todo',
                           'prefix_reference': 'https://example.org/todo/'}},
     'source_file': 'def/events.yaml',
     'title': 'Todo Domain Events Data Model'} )


class DomainEvent(ConfiguredBaseModel):
    """
    Base class for all domain events - immutable facts about what happened. This is an abstract class that should be extended by concrete event types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/events'})

    pass


class Todo(ConfiguredBaseModel):
    """
    Represents a todo item with text and completion status
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo'})

    id: str = Field(default=..., description="""Unique identifier for the todo item""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo']} })
    text: str = Field(default=..., description="""The text content of the todo item""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo', 'TodoAdded']} })
    completed: bool = Field(default=..., description="""Whether the todo has been completed""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the todo was created""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo', 'TodoAdded']} })
    completed_at: Optional[datetime ] = Field(default=None, description="""Timestamp when the todo was completed""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo', 'TodoCompleted']} })


class TodoAdded(DomainEvent):
    """
    Event recording that a todo item was added
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo/events'})

    todo_id: str = Field(default=..., description="""ID of the todo that was added""", json_schema_extra = { "linkml_meta": {'domain_of': ['TodoAdded', 'TodoCompleted', 'TodoDeleted']} })
    text: str = Field(default=..., description="""Text of the todo""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo', 'TodoAdded']} })
    created_at: datetime  = Field(default=..., description="""When the todo was created""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo', 'TodoAdded']} })


class TodoCompleted(DomainEvent):
    """
    Event recording that a todo item was marked as completed
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo/events'})

    todo_id: str = Field(default=..., description="""ID of the todo item that was completed""", json_schema_extra = { "linkml_meta": {'domain_of': ['TodoAdded', 'TodoCompleted', 'TodoDeleted']} })
    completed_at: datetime  = Field(default=..., description="""Timestamp when the todo was completed""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo', 'TodoCompleted']} })


class TodoDeleted(DomainEvent):
    """
    Event recording that a todo item was deleted
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo/events'})

    todo_id: str = Field(default=..., description="""ID of the todo item that was deleted""", json_schema_extra = { "linkml_meta": {'domain_of': ['TodoAdded', 'TodoCompleted', 'TodoDeleted']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
DomainEvent.model_rebuild()
Todo.model_rebuild()
TodoAdded.model_rebuild()
TodoCompleted.model_rebuild()
TodoDeleted.model_rebuild()
