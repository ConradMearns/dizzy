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
     'description': 'LinkML schema for query objects that define inputs and '
                    'outputs for querying drives, partitions, and file items.',
     'id': 'https://example.org/dedupe/queries',
     'imports': ['linkml:types'],
     'name': 'dedupe-queries-schema',
     'prefixes': {'dedupe': {'prefix_prefix': 'dedupe',
                             'prefix_reference': 'https://example.org/dedupe/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'def/queries.yaml',
     'title': 'Dedupe Queries Data Model'} )


class QueryInput(ConfiguredBaseModel):
    """
    Base class for all query input parameter objects
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dedupe/queries'})

    pass


class Query(ConfiguredBaseModel):
    """
    Base class for all query result objects
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dedupe/queries'})

    pass


class ListHardDrivesInput(QueryInput):
    """
    Input parameters for listing all hard drives
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    pass


class ListHardDrives(Query):
    """
    Query result containing a list of hard drives
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    drives: list[str] = Field(default=..., description="""List of hard drives found""", json_schema_extra = { "linkml_meta": {'alias': 'drives', 'domain_of': ['ListHardDrives']} })


class ListPartitionsInput(QueryInput):
    """
    Input parameters for listing partitions
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    drive_uuid: Optional[str] = Field(default=None, description="""UUID of the hard drive to filter by (optional - if not provided, lists all partitions)""", json_schema_extra = { "linkml_meta": {'alias': 'drive_uuid', 'domain_of': ['ListPartitionsInput']} })


class ListPartitions(Query):
    """
    Query result containing a list of partitions
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    partitions: list[str] = Field(default=..., description="""List of partitions found""", json_schema_extra = { "linkml_meta": {'alias': 'partitions', 'domain_of': ['ListPartitions']} })


class ListFileItemsInput(QueryInput):
    """
    Input parameters for listing file items in a partition
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    partition_uuid: str = Field(default=..., description="""UUID of the partition to list files from""", json_schema_extra = { "linkml_meta": {'alias': 'partition_uuid', 'domain_of': ['ListFileItemsInput']} })


class ListFileItems(Query):
    """
    Query result containing a list of file items
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    file_items: list[str] = Field(default=..., description="""List of file items found""", json_schema_extra = { "linkml_meta": {'alias': 'file_items', 'domain_of': ['ListFileItems']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
QueryInput.model_rebuild()
Query.model_rebuild()
ListHardDrivesInput.model_rebuild()
ListHardDrives.model_rebuild()
ListPartitionsInput.model_rebuild()
ListPartitions.model_rebuild()
ListFileItemsInput.model_rebuild()
ListFileItems.model_rebuild()

