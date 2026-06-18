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


linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/queries/get_step_inputs/',
     'default_range': 'string',
     'description': "The typed inputs of a recipe's steps, as parallel lists",
     'id': 'https://example.org/queries/get_step_inputs',
     'imports': ['linkml:types'],
     'name': 'get_step_inputs',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': '../examples/recipes/def/queries/get_step_inputs.yaml'} )


class GetStepInputsInput(ConfiguredBaseModel):
    """
    Input for get_step_inputs
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/queries/get_step_inputs'})

    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['GetStepInputsInput']} })


class GetStepInputsOutput(ConfiguredBaseModel):
    """
    Output for get_step_inputs — one entry per step input, as parallel lists
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/queries/get_step_inputs'})

    step_orders: Optional[list[int]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['GetStepInputsOutput']} })
    ingredient_types: Optional[list[str]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['GetStepInputsOutput']} })
    qtys: Optional[list[Decimal]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['GetStepInputsOutput']} })
    units: Optional[list[str]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['GetStepInputsOutput']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
GetStepInputsInput.model_rebuild()
GetStepInputsOutput.model_rebuild()
