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
     'description': 'LinkML meta-schema defining the structure of libconfig.yaml '
                    'files used to configure which dizzy elements are implemented '
                    'in which language runtimes.',
     'id': 'https://example.org/dizzy/libconfig',
     'imports': ['linkml:types'],
     'name': 'dizzy-libconfig-schema',
     'prefixes': {'dizzy': {'prefix_prefix': 'dizzy',
                            'prefix_reference': 'https://example.org/dizzy/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'dizzy/src/dizzy/def/libconfig.yaml',
     'title': 'Dizzy Library Configuration Schema'} )

class LanguageRuntime(str, Enum):
    """
    Supported language runtime patterns
    """
    python_uv = "python-uv"
    """
    Python with uv and pyproject.toml
    """
    rust_cargo = "rust-cargo"
    """
    Rust with Cargo.toml
    """
    typescript_npm = "typescript-npm"
    """
    TypeScript with package.json and tsconfig.json
    """



class LibConfig(ConfiguredBaseModel):
    """
    Top-level container for a Dizzy library configuration file.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/libconfig'})

    procedures: Optional[list[ElementBinding]] = Field(default=[], description="""Procedure bindings to language runtimes""", json_schema_extra = { "linkml_meta": {'domain_of': ['LibConfig']} })
    policies: Optional[list[ElementBinding]] = Field(default=[], description="""Policy bindings to language runtimes""", json_schema_extra = { "linkml_meta": {'domain_of': ['LibConfig']} })
    queries: Optional[list[ElementBinding]] = Field(default=[], description="""Query bindings to language runtimes""", json_schema_extra = { "linkml_meta": {'domain_of': ['LibConfig']} })
    projections: Optional[list[ElementBinding]] = Field(default=[], description="""Projection bindings to language runtimes""", json_schema_extra = { "linkml_meta": {'domain_of': ['LibConfig']} })


class ElementBinding(ConfiguredBaseModel):
    """
    Binds a named element to one or more language runtimes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dizzy/libconfig'})

    name: str = Field(default=..., description="""Element name matching a name in the corresponding feat section""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementBinding']} })
    runtimes: Optional[list[LanguageRuntime]] = Field(default=[], description="""Language runtimes that implement this element""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementBinding']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
LibConfig.model_rebuild()
ElementBinding.model_rebuild()
