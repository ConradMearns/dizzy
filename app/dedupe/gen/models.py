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
     'description': 'LinkML schema for tracking hard drives, partitions, and '
                    'filesystem items for deduplication purposes.',
     'id': 'https://example.org/dedupe',
     'imports': ['linkml:types'],
     'name': 'dedupe-schema',
     'prefixes': {'dedupe': {'prefix_prefix': 'dedupe',
                             'prefix_reference': 'https://example.org/dedupe/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'def/models.yaml',
     'title': 'Dedupe Data Model'} )


class HardDrive(ConfiguredBaseModel):
    """
    Represents a physical or logical hard drive with a unique identifier
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe'})

    uuid: str = Field(default=..., description="""Unique identifier for the hard drive""", json_schema_extra = { "linkml_meta": {'alias': 'uuid', 'domain_of': ['HardDrive', 'Partition']} })
    label: Optional[str] = Field(default=None, description="""Optional human-readable label for the drive""", json_schema_extra = { "linkml_meta": {'alias': 'label', 'domain_of': ['HardDrive', 'Partition']} })
    size_bytes: Optional[int] = Field(default=None, description="""Total size of the hard drive in bytes""", json_schema_extra = { "linkml_meta": {'alias': 'size_bytes', 'domain_of': ['HardDrive', 'Partition', 'FileItem']} })


class Partition(ConfiguredBaseModel):
    """
    Represents a partition on a hard drive
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe'})

    uuid: str = Field(default=..., description="""Unique identifier for the partition""", json_schema_extra = { "linkml_meta": {'alias': 'uuid', 'domain_of': ['HardDrive', 'Partition']} })
    drive_uuid: str = Field(default=..., description="""UUID of the hard drive containing this partition""", json_schema_extra = { "linkml_meta": {'alias': 'drive_uuid', 'domain_of': ['Partition', 'FileItem']} })
    label: Optional[str] = Field(default=None, description="""Optional human-readable label for the partition""", json_schema_extra = { "linkml_meta": {'alias': 'label', 'domain_of': ['HardDrive', 'Partition']} })
    mount_point: Optional[str] = Field(default=None, description="""Optional mount point where partition is mounted""", json_schema_extra = { "linkml_meta": {'alias': 'mount_point', 'domain_of': ['Partition']} })
    size_bytes: Optional[int] = Field(default=None, description="""Total size of the partition in bytes""", json_schema_extra = { "linkml_meta": {'alias': 'size_bytes', 'domain_of': ['HardDrive', 'Partition', 'FileItem']} })


class FileItem(ConfiguredBaseModel):
    """
    Represents a file or directory item found on a partition
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe'})

    id: str = Field(default=..., description="""Unique identifier for this file item record""", json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['FileItem']} })
    drive_uuid: str = Field(default=..., description="""UUID of the hard drive where item was found""", json_schema_extra = { "linkml_meta": {'alias': 'drive_uuid', 'domain_of': ['Partition', 'FileItem']} })
    partition_uuid: str = Field(default=..., description="""UUID of the partition where item was found""", json_schema_extra = { "linkml_meta": {'alias': 'partition_uuid', 'domain_of': ['FileItem']} })
    path: str = Field(default=..., description="""Full path of the item on the partition""", json_schema_extra = { "linkml_meta": {'alias': 'path', 'domain_of': ['FileItem']} })
    size_bytes: int = Field(default=..., description="""Size of the item in bytes""", json_schema_extra = { "linkml_meta": {'alias': 'size_bytes', 'domain_of': ['HardDrive', 'Partition', 'FileItem']} })
    hash: str = Field(default=..., description="""Hash of the item contents (e.g., SHA256, MD5)""", json_schema_extra = { "linkml_meta": {'alias': 'hash', 'domain_of': ['FileItem']} })
    hash_algorithm: Optional[str] = Field(default=None, description="""Algorithm used to generate the hash""", json_schema_extra = { "linkml_meta": {'alias': 'hash_algorithm', 'domain_of': ['FileItem']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
HardDrive.model_rebuild()
Partition.model_rebuild()
FileItem.model_rebuild()

