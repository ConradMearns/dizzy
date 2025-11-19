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
     'description': 'LinkML schema for query objects that retrieve todo '
                    'information',
     'id': 'https://example.org/todo/queries',
     'imports': ['linkml:types',
                 '../../../pkg/dizzy/src/dizzy/def/queries',
                 'models'],
     'name': 'todo-queries-schema',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'todo': {'prefix_prefix': 'todo',
                           'prefix_reference': 'https://example.org/todo/'}},
     'source_file': 'def/queries.yaml',
     'title': 'Todo Queries Data Model'} )


class QueryInput(ConfiguredBaseModel):
    """
    Base class for all query input parameter objects. This is an abstract class that should be extended by concrete input types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/queries'})

    pass


class Query(ConfiguredBaseModel):
    """
    Base class for all query result objects. This is an abstract class that should be extended by concrete result types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/queries'})

    pass


class Todo(ConfiguredBaseModel):
    """
    Represents a todo item with text and completion status
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo'})

    id: str = Field(default=..., description="""Unique identifier for the todo item""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo']} })
    text: str = Field(default=..., description="""The text content of the todo item""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo']} })
    completed: bool = Field(default=..., description="""Whether the todo has been completed""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the todo was created""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo']} })
    completed_at: Optional[datetime ] = Field(default=None, description="""Timestamp when the todo was completed""", json_schema_extra = { "linkml_meta": {'domain_of': ['Todo']} })


class ListTodosInput(QueryInput):
    """
    Input for listing all todos
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo/queries'})

    include_completed: Optional[bool] = Field(default=None, description="""Whether to include completed todos""", json_schema_extra = { "linkml_meta": {'domain_of': ['ListTodosInput']} })


class ListTodos(Query):
    """
    Query result containing list of todos
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo/queries'})

    todos: list[str] = Field(default=..., description="""List of all todos""", json_schema_extra = { "linkml_meta": {'domain_of': ['ListTodos']} })


class GetTodoInput(QueryInput):
    """
    Input for getting a specific todo by ID
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo/queries'})

    todo_id: str = Field(default=..., description="""ID of the todo to retrieve""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetTodoInput']} })


class GetTodo(Query):
    """
    Query result containing a single todo
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/todo/queries'})

    todo: Optional[str] = Field(default=None, description="""The requested todo""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetTodo']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
QueryInput.model_rebuild()
Query.model_rebuild()
Todo.model_rebuild()
ListTodosInput.model_rebuild()
ListTodos.model_rebuild()
GetTodoInput.model_rebuild()
GetTodo.model_rebuild()
