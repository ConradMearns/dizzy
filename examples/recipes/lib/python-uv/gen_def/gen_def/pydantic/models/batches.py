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


linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/models/batches/',
     'default_range': 'string',
     'description': 'Batches — durable running instances of recipes, with status',
     'id': 'https://example.org/models/batches',
     'imports': ['linkml:types'],
     'name': 'batches',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': '../examples/recipes/def/models/batches.yaml'} )


class Batch(ConfiguredBaseModel):
    """
    A durable running instance of a recipe
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/models/batches'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Batch']} })
    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Batch']} })
    requires_type: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Batch']} })
    status: str = Field(default=..., description="""ready | blocked | completed""", json_schema_extra = { "linkml_meta": {'domain_of': ['Batch']} })
    opened_at: datetime  = Field(default=..., description="""When the batch was opened — the FIFO key for unblocking""", json_schema_extra = { "linkml_meta": {'domain_of': ['Batch']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Batch.model_rebuild()
