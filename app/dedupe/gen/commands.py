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
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




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
     'description': 'LinkML schema for command objects that represent operations '
                    'to be performed on drives and partitions.',
     'id': 'https://example.org/dedupe/commands',
     'imports': ['linkml:types'],
     'name': 'dedupe-commands-schema',
     'prefixes': {'dedupe': {'prefix_prefix': 'dedupe',
                             'prefix_reference': 'https://example.org/dedupe/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'def/commands.yaml',
     'title': 'Dedupe Commands Data Model'} )


class Command(ConfiguredBaseModel):
    """
    Base class for all commands that can be executed in the dedupe system
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/commands'})

    pass


class ScanPartition(Command):
    """
    Command to scan a specific partition and catalog all files
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/commands'})

    partition_uuid: str = Field(default=..., description="""UUID of the partition to scan""", json_schema_extra = { "linkml_meta": {'alias': 'partition_uuid', 'domain_of': ['ScanPartition']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Command.model_rebuild()
ScanPartition.model_rebuild()

