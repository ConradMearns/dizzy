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


linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/models/catalog/',
     'default_range': 'string',
     'description': 'Ingredients, tools, recipes, and the typed steps & inputs of '
                    'each recipe',
     'id': 'https://example.org/models/catalog',
     'imports': ['linkml:types'],
     'name': 'catalog',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': '../examples/recipes/def/models/catalog.yaml'} )


class Ingredient(ConfiguredBaseModel):
    """
    A pantry ingredient type
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/models/catalog'})

    ingredient_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Ingredient', 'StepInput']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Ingredient', 'Tool', 'Recipe']} })
    unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Ingredient', 'StepInput']} })


class Tool(ConfiguredBaseModel):
    """
    A tool used to perform recipe steps (a PROV agent)
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/models/catalog'})

    tool_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Tool', 'RecipeStep']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Ingredient', 'Tool', 'Recipe']} })


class Recipe(ConfiguredBaseModel):
    """
    A recipe header
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/models/catalog'})

    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Recipe', 'RecipeStep', 'StepInput']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Ingredient', 'Tool', 'Recipe']} })
    requires_type: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Recipe']} })
    output_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Recipe']} })
    output_unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Recipe']} })


class RecipeStep(ConfiguredBaseModel):
    """
    One ordered, structured step of a recipe
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/models/catalog'})

    id: str = Field(default=..., description="""Composite key, \"<recipe_id>#<step_order>\"""", json_schema_extra = { "linkml_meta": {'domain_of': ['RecipeStep', 'StepInput']} })
    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Recipe', 'RecipeStep', 'StepInput']} })
    step_order: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['RecipeStep', 'StepInput']} })
    activity_kind: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['RecipeStep']} })
    tool_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Tool', 'RecipeStep']} })


class StepInput(ConfiguredBaseModel):
    """
    One typed input consumed by a recipe step
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/models/catalog'})

    id: str = Field(default=..., description="""Composite key, \"<recipe_id>#<step_order>#<ingredient_type>\"""", json_schema_extra = { "linkml_meta": {'domain_of': ['RecipeStep', 'StepInput']} })
    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Recipe', 'RecipeStep', 'StepInput']} })
    step_order: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['RecipeStep', 'StepInput']} })
    ingredient_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Ingredient', 'StepInput']} })
    qty: Decimal = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['StepInput']} })
    unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Ingredient', 'StepInput']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Ingredient.model_rebuild()
Tool.model_rebuild()
Recipe.model_rebuild()
RecipeStep.model_rebuild()
StepInput.model_rebuild()
