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
     'description': 'LinkML schema for mutation objects that represent state '
                    'changes in the system',
     'id': 'https://example.org/todo/mutations',
     'imports': ['linkml:types',
                 '../../../pkg/dizzy/src/dizzy/def/mutations',
                 'models'],
     'name': 'todo-mutations-schema',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'todo': {'prefix_prefix': 'todo',
                           'prefix_reference': 'https://example.org/todo/'}},
     'source_file': 'def/mutations.yaml',
     'title': 'Todo Mutations Data Model'} )


class MutationInput(ConfiguredBaseModel):
    """
    Base class for all mutation input parameter objects. This is an abstract class that should be extended by concrete input types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/mutations'})

    pass


class Mutation(ConfiguredBaseModel):
    """
    Base class for all mutation result objects. This is an abstract class that should be extended by concrete result types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/mutations'})

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


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
MutationInput.model_rebuild()
Mutation.model_rebuild()
Todo.model_rebuild()
