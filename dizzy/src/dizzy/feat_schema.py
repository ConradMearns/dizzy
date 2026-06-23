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


linkml_meta = LinkMLMeta({'default_prefix': 'dizzy',
     'default_range': 'string',
     'description': 'LinkML meta-schema formally defining the structure of '
                    '.feat.yaml feature definition files used by the Dizzy '
                    'generator pipeline.',
     'id': 'https://example.org/dizzy/feat',
     'imports': ['linkml:types'],
     'name': 'dizzy-feat-schema',
     'prefixes': {'dizzy': {'prefix_prefix': 'dizzy',
                            'prefix_reference': 'https://example.org/dizzy/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'dizzy/src/dizzy/def/feat.yaml',
     'title': 'Dizzy Feature Definition Meta-Schema'} )


class FeatureDefinition(ConfiguredBaseModel):
    """
    Top-level container for a Dizzy feature definition file.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    description: Optional[str] = Field(default=None, description="""Human-readable description of the feature""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    models: Optional[list[ModelDef]] = Field(default=[], description="""Named database schemas""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    queries: Optional[list[QueryDef]] = Field(default=[], description="""Named read operations""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition', 'ProcedureDef', 'PolicyDef']} })
    commands: Optional[list[CommandDef]] = Field(default=[], description="""Named write intents""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    events: Optional[list[EventDef]] = Field(default=[], description="""Immutable domain facts""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    procedures: Optional[list[ProcedureDef]] = Field(default=[], description="""Command handlers""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    policies: Optional[list[PolicyDef]] = Field(default=[], description="""Event-driven reaction handlers""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    projections: Optional[list[ProjectionDef]] = Field(default=[], description="""Read-model builders""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition']} })
    environment: Optional[list[EnvironmentDef]] = Field(default=[], description="""Named injected constants/variables, acquired in place of os env vars. Each names a shape authored in def/environment.yaml.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    telemetry: Optional[list[TelemetryDef]] = Field(default=[], description="""Named host-injected observation sinks (callables). Each names the payload shape authored in def/telemetry.yaml.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


class EnvironmentDef(ConfiguredBaseModel):
    """
    A named injected constant/variable available to functions in place of an os environment variable. Its shape is authored in def/environment.yaml.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Environment entry name (snake_case)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: Optional[str] = Field(default=None, description="""Human-readable description of the environment entry""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


class TelemetryDef(ConfiguredBaseModel):
    """
    A named host-injected observation sink. The function calls it with a typed payload whose shape is authored in def/telemetry.yaml.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Telemetry sink name (snake_case)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: Optional[str] = Field(default=None, description="""Human-readable description of the telemetry sink""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


class ModelDef(ConfiguredBaseModel):
    """
    A named database schema declaration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Schema name (plural, lowercase, snake_case)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: Optional[str] = Field(default=None, description="""Human-readable description of the schema""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    adapters: Optional[list[str]] = Field(default=[], description="""Named adapter bindings for this model""", json_schema_extra = { "linkml_meta": {'domain_of': ['ModelDef']} })


class QueryDef(ConfiguredBaseModel):
    """
    A named read operation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Query name (snake_case)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: str = Field(default=..., description="""Human-readable description of the query""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    model: Optional[str] = Field(default=None, description="""The schema name from models that this query reads from""", json_schema_extra = { "linkml_meta": {'domain_of': ['QueryDef', 'ProjectionDef']} })
    adapter: Optional[str] = Field(default=None, description="""The adapter name on the model that this query uses""", json_schema_extra = { "linkml_meta": {'domain_of': ['QueryDef', 'ProjectionDef']} })
    environment: Optional[list[str]] = Field(default=[], description="""Environment entry names this querier needs injected""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    telemetry: Optional[list[str]] = Field(default=[], description="""Telemetry sink names this querier may call""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


class CommandDef(ConfiguredBaseModel):
    """
    A named write intent.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Command name (snake_case)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: Optional[str] = Field(default=None, description="""Human-readable description of the command""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


class EventDef(ConfiguredBaseModel):
    """
    An immutable domain fact.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Event name (snake_case, past-tense)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: Optional[str] = Field(default=None, description="""Human-readable description of the event""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


class ProcedureDef(ConfiguredBaseModel):
    """
    A command handler that processes exactly one command, may use queries, and emits events.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Procedure name (snake_case)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: Optional[str] = Field(default=None, description="""Human-readable description of the procedure logic""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    command: str = Field(default=..., description="""The command name this procedure handles""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProcedureDef']} })
    queries: Optional[list[str]] = Field(default=[], description="""Query names this procedure needs access to""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition', 'ProcedureDef', 'PolicyDef']} })
    emits: Optional[list[str]] = Field(default=[], description="""Event names this procedure may emit""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProcedureDef', 'PolicyDef']} })
    environment: Optional[list[str]] = Field(default=[], description="""Environment entry names this procedure needs injected""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    telemetry: Optional[list[str]] = Field(default=[], description="""Telemetry sink names this procedure may call""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


class PolicyDef(ConfiguredBaseModel):
    """
    An event-driven reaction handler that listens to exactly one event, may use queries and optionally dispatches commands.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Policy name (snake_case)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: Optional[str] = Field(default=None, description="""Human-readable description of the policy logic""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    event: str = Field(default=..., description="""The event name that triggers this policy""", json_schema_extra = { "linkml_meta": {'domain_of': ['PolicyDef', 'ProjectionDef']} })
    queries: Optional[list[str]] = Field(default=[], description="""Query names this policy needs access to""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition', 'ProcedureDef', 'PolicyDef']} })
    emits: Optional[list[str]] = Field(default=[], description="""Command names this policy may dispatch""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProcedureDef', 'PolicyDef']} })
    environment: Optional[list[str]] = Field(default=[], description="""Environment entry names this policy needs injected""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    telemetry: Optional[list[str]] = Field(default=[], description="""Telemetry sink names this policy may call""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


class ProjectionDef(ConfiguredBaseModel):
    """
    A read-model builder that responds to a single event and writes into one model schema via a named adapter.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/feat'})

    name: str = Field(default=..., description="""Projection name (snake_case)""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    description: str = Field(default=..., description="""Human-readable description of what this projection does""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'EnvironmentDef',
                       'TelemetryDef',
                       'ModelDef',
                       'QueryDef',
                       'CommandDef',
                       'EventDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    event: str = Field(default=..., description="""The single event that triggers this projection""", json_schema_extra = { "linkml_meta": {'domain_of': ['PolicyDef', 'ProjectionDef']} })
    model: Optional[str] = Field(default=None, description="""The schema name from models that this projection writes into""", json_schema_extra = { "linkml_meta": {'domain_of': ['QueryDef', 'ProjectionDef']} })
    adapter: Optional[str] = Field(default=None, description="""The adapter name on the model that this projection uses""", json_schema_extra = { "linkml_meta": {'domain_of': ['QueryDef', 'ProjectionDef']} })
    environment: Optional[list[str]] = Field(default=[], description="""Environment entry names this projection needs injected""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })
    telemetry: Optional[list[str]] = Field(default=[], description="""Telemetry sink names this projection may call""", json_schema_extra = { "linkml_meta": {'domain_of': ['FeatureDefinition',
                       'QueryDef',
                       'ProcedureDef',
                       'PolicyDef',
                       'ProjectionDef']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
FeatureDefinition.model_rebuild()
EnvironmentDef.model_rebuild()
TelemetryDef.model_rebuild()
ModelDef.model_rebuild()
QueryDef.model_rebuild()
CommandDef.model_rebuild()
EventDef.model_rebuild()
ProcedureDef.model_rebuild()
PolicyDef.model_rebuild()
ProjectionDef.model_rebuild()
