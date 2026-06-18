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


linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/commands/',
     'default_range': 'string',
     'id': 'https://example.org/commands',
     'imports': ['linkml:types'],
     'name': 'commands',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': '../examples/recipes/def/commands.yaml'} )


class RegisterIngredient(ConfiguredBaseModel):
    """
    Add an ingredient type to the pantry catalog
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/commands'})

    ingredient_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['register_ingredient', 'add_step_input']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['register_ingredient', 'register_tool', 'define_recipe']} })
    unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['register_ingredient', 'add_step_input']} })


class RegisterTool(ConfiguredBaseModel):
    """
    Add a tool (a PROV agent) to the catalog
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/commands'})

    tool_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['register_tool', 'add_recipe_step']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['register_ingredient', 'register_tool', 'define_recipe']} })


class DefineRecipe(ConfiguredBaseModel):
    """
    Declare a recipe header — what it yields and what upstream entity it requires
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/commands'})

    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['define_recipe',
                       'add_recipe_step',
                       'add_step_input',
                       'start_batch']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['register_ingredient', 'register_tool', 'define_recipe']} })
    requires_type: Optional[str] = Field(default=None, description="""The upstream entity type this recipe consumes; empty for a root recipe""", json_schema_extra = { "linkml_meta": {'domain_of': ['define_recipe']} })
    output_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['define_recipe']} })
    output_unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['define_recipe']} })


class AddRecipeStep(ConfiguredBaseModel):
    """
    Add one ordered, structured step to a recipe
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/commands'})

    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['define_recipe',
                       'add_recipe_step',
                       'add_step_input',
                       'start_batch']} })
    step_order: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['add_recipe_step', 'add_step_input']} })
    activity_kind: str = Field(default=..., description="""What the step does, e.g. mix, ferment, bake, toss""", json_schema_extra = { "linkml_meta": {'domain_of': ['add_recipe_step']} })
    tool_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['register_tool', 'add_recipe_step']} })


class AddStepInput(ConfiguredBaseModel):
    """
    Declare one typed input a recipe step consumes
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/commands'})

    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['define_recipe',
                       'add_recipe_step',
                       'add_step_input',
                       'start_batch']} })
    step_order: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['add_recipe_step', 'add_step_input']} })
    ingredient_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['register_ingredient', 'add_step_input']} })
    qty: Decimal = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['add_step_input']} })
    unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['register_ingredient', 'add_step_input']} })


class StartBatch(ConfiguredBaseModel):
    """
    Open a batch — a durable running instance of a recipe
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/commands'})

    batch_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['start_batch', 'advance_batch']} })
    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['define_recipe',
                       'add_recipe_step',
                       'add_step_input',
                       'start_batch']} })


class AdvanceBatch(ConfiguredBaseModel):
    """
    Run a batch's steps to completion, producing its output entity
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/commands'})

    batch_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['start_batch', 'advance_batch']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
RegisterIngredient.model_rebuild()
RegisterTool.model_rebuild()
DefineRecipe.model_rebuild()
AddRecipeStep.model_rebuild()
AddStepInput.model_rebuild()
StartBatch.model_rebuild()
AdvanceBatch.model_rebuild()
