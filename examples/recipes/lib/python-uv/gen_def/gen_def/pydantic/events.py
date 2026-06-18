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


linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/events/',
     'default_range': 'string',
     'id': 'https://example.org/events',
     'imports': ['linkml:types'],
     'name': 'events',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': '../examples/recipes/def/events.yaml'} )


class IngredientRegistered(ConfiguredBaseModel):
    """
    An ingredient type was added to the pantry
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    ingredient_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ingredient_registered', 'step_input_added']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ingredient_registered', 'tool_registered', 'recipe_defined']} })
    unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ingredient_registered', 'step_input_added', 'entity_produced']} })


class ToolRegistered(ConfiguredBaseModel):
    """
    A tool was added to the catalog
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    tool_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['tool_registered', 'recipe_step_added', 'step_performed']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ingredient_registered', 'tool_registered', 'recipe_defined']} })


class RecipeDefined(ConfiguredBaseModel):
    """
    A recipe header was declared
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_defined',
                       'recipe_step_added',
                       'step_input_added',
                       'batch_opened']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ingredient_registered', 'tool_registered', 'recipe_defined']} })
    requires_type: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_defined', 'batch_opened']} })
    output_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_defined']} })
    output_unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_defined']} })


class RecipeStepAdded(ConfiguredBaseModel):
    """
    A structured step was added to a recipe
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_defined',
                       'recipe_step_added',
                       'step_input_added',
                       'batch_opened']} })
    step_order: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_step_added', 'step_input_added', 'step_performed']} })
    activity_kind: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_step_added', 'step_performed']} })
    tool_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['tool_registered', 'recipe_step_added', 'step_performed']} })


class StepInputAdded(ConfiguredBaseModel):
    """
    A typed input was declared for a recipe step
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_defined',
                       'recipe_step_added',
                       'step_input_added',
                       'batch_opened']} })
    step_order: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_step_added', 'step_input_added', 'step_performed']} })
    ingredient_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ingredient_registered', 'step_input_added']} })
    qty: Decimal = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['step_input_added', 'entity_produced']} })
    unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ingredient_registered', 'step_input_added', 'entity_produced']} })


class BatchOpened(ConfiguredBaseModel):
    """
    A batch was opened, either ready to run or blocked on a missing entity
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    batch_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_opened',
                       'step_performed',
                       'entity_produced',
                       'batch_completed',
                       'batch_run_failed']} })
    recipe_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_defined',
                       'recipe_step_added',
                       'step_input_added',
                       'batch_opened']} })
    requires_type: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_defined', 'batch_opened']} })
    status: str = Field(default=..., description="""ready | blocked""", json_schema_extra = { "linkml_meta": {'domain_of': ['batch_opened']} })
    opened_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_opened']} })


class StepPerformed(ConfiguredBaseModel):
    """
    A recipe step was executed by a tool (prov:wasAssociatedWith)
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    activity_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['step_performed', 'entity_consumed', 'entity_produced']} })
    batch_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_opened',
                       'step_performed',
                       'entity_produced',
                       'batch_completed',
                       'batch_run_failed']} })
    step_order: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_step_added', 'step_input_added', 'step_performed']} })
    activity_kind: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['recipe_step_added', 'step_performed']} })
    tool_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['tool_registered', 'recipe_step_added', 'step_performed']} })
    performed_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['step_performed']} })


class EntityConsumed(ConfiguredBaseModel):
    """
    A step consumed an entity (prov:used)
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    activity_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['step_performed', 'entity_consumed', 'entity_produced']} })
    entity_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['entity_consumed', 'entity_produced']} })
    entity_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['entity_consumed', 'entity_produced']} })
    role: str = Field(default=..., description="""How the entity was used, e.g. ingredient or upstream""", json_schema_extra = { "linkml_meta": {'domain_of': ['entity_consumed']} })


class EntityProduced(ConfiguredBaseModel):
    """
    A batch produced an output entity (prov:wasGeneratedBy)
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    entity_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['entity_consumed', 'entity_produced']} })
    activity_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['step_performed', 'entity_consumed', 'entity_produced']} })
    batch_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_opened',
                       'step_performed',
                       'entity_produced',
                       'batch_completed',
                       'batch_run_failed']} })
    entity_type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['entity_consumed', 'entity_produced']} })
    qty: Decimal = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['step_input_added', 'entity_produced']} })
    unit: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ingredient_registered', 'step_input_added', 'entity_produced']} })
    produced_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['entity_produced']} })


class EntityDerived(ConfiguredBaseModel):
    """
    An output entity was derived from a source (prov:wasDerivedFrom)
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    output_entity_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['entity_derived']} })
    source_entity_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['entity_derived']} })


class BatchCompleted(ConfiguredBaseModel):
    """
    A batch finished running all of its steps
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    batch_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_opened',
                       'step_performed',
                       'entity_produced',
                       'batch_completed',
                       'batch_run_failed']} })
    completed_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_completed']} })


class BatchRunFailed(ConfiguredBaseModel):
    """
    A batch could not run because a required entity was unavailable
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/events'})

    batch_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_opened',
                       'step_performed',
                       'entity_produced',
                       'batch_completed',
                       'batch_run_failed']} })
    reason: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_run_failed']} })
    failed_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['batch_run_failed']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
IngredientRegistered.model_rebuild()
ToolRegistered.model_rebuild()
RecipeDefined.model_rebuild()
RecipeStepAdded.model_rebuild()
StepInputAdded.model_rebuild()
BatchOpened.model_rebuild()
StepPerformed.model_rebuild()
EntityConsumed.model_rebuild()
EntityProduced.model_rebuild()
EntityDerived.model_rebuild()
BatchCompleted.model_rebuild()
BatchRunFailed.model_rebuild()
