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


linkml_meta = LinkMLMeta({'default_prefix': 'dedupe',
     'default_range': 'string',
     'description': 'LinkML schema for defining application features with '
                    'commands, events, procedures, and policies. This schema '
                    'allows modeling event-driven workflows and command-event '
                    'chains.',
     'id': 'https://example.org/dedupe/feature-definition',
     'imports': ['linkml:types'],
     'name': 'feature-definition-schema',
     'prefixes': {'dedupe': {'prefix_prefix': 'dedupe',
                             'prefix_reference': 'https://example.org/dedupe/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'app/dedupe/feature_definition.schema.yaml',
     'title': 'Feature Definition Data Model'} )


class FeatureDefinition(ConfiguredBaseModel):
    """
    Root class representing a complete feature definition with commands, events, procedures, and policies.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/feature-definition',
         'tree_root': True})

    description: Optional[str] = Field(default=None, description="""Human-readable description of the feature""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition', 'Procedure', 'Policy']} })
    commands: Optional[list[str]] = Field(default=[], description="""Map of command names to their descriptions""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    events: Optional[list[str]] = Field(default=[], description="""Map of event names to their descriptions""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    procedures: Optional[list[Procedure]] = Field(default=[], description="""Map of procedure names to procedure definitions""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    policies: Optional[list[Policy]] = Field(default=[], description="""Map of policy names to policy definitions""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })


class Procedure(ConfiguredBaseModel):
    """
    A procedure that responds to a command and emits events. Procedures perform the actual work of the system.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/feature-definition'})

    description: Optional[str] = Field(default=None, description="""Human-readable description of what this procedure does""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition', 'Procedure', 'Policy']} })
    command: Optional[str] = Field(default=None, description="""The command that triggers this procedure""", json_schema_extra = { "linkml_meta": {'domain_of': ['Procedure']} })
    emits: Optional[list[str]] = Field(default=[], description="""List of events this procedure can emit""", json_schema_extra = { "linkml_meta": {'domain_of': ['Procedure', 'Policy']} })


class Policy(ConfiguredBaseModel):
    """
    A policy that responds to events and may issue commands. Policies implement business logic and orchestration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/feature-definition'})

    description: Optional[str] = Field(default=None, description="""Human-readable description of what this policy does""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition', 'Procedure', 'Policy']} })
    event: Optional[str] = Field(default=None, description="""The event that triggers this policy""", json_schema_extra = { "linkml_meta": {'domain_of': ['Policy']} })
    emits: Optional[list[str]] = Field(default=[], description="""List of commands this policy can emit""", json_schema_extra = { "linkml_meta": {'domain_of': ['Procedure', 'Policy']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
FeatureDefinition.model_rebuild()
Procedure.model_rebuild()
Policy.model_rebuild()
