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
     'description': 'LinkML schema for command objects that represent operations '
                    'to be performed on drives and partitions.',
     'id': 'https://example.org/dedupe/commands',
     'imports': ['linkml:types',
                 '../../../pkg/dizzy/src/dizzy/def/commands',
                 'models'],
     'name': 'dedupe-commands-schema',
     'prefixes': {'dedupe': {'prefix_prefix': 'dedupe',
                             'prefix_reference': 'https://example.org/dedupe/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': '/home/conrad/dizzy/app/dedupe/def/commands.yaml',
     'title': 'Dedupe Commands Data Model'} )


class Command(ConfiguredBaseModel):
    """
    Base class for all commands that can be executed. This is an abstract class that should be extended by concrete command types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/commands'})

    pass


class HardDrive(ConfiguredBaseModel):
    """
    Represents a physical or logical hard drive with a unique identifier
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe'})

    uuid: str = Field(default=..., description="""Unique identifier for the hard drive""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition']} })
    label: Optional[str] = Field(default=None, description="""Optional human-readable label for the drive""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition']} })
    size_bytes: Optional[int] = Field(default=None, description="""Total size of the hard drive in bytes""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition', 'FileItem']} })


class Partition(ConfiguredBaseModel):
    """
    Represents a partition on a hard drive
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe'})

    uuid: str = Field(default=..., description="""Unique identifier for the partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition']} })
    drive_uuid: str = Field(default=..., description="""UUID of the hard drive containing this partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'FileItem']} })
    label: Optional[str] = Field(default=None, description="""Optional human-readable label for the partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition']} })
    mount_point: Optional[str] = Field(default=None, description="""Optional mount point where partition is mounted""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'AssignPartitionMount']} })
    size_bytes: Optional[int] = Field(default=None, description="""Total size of the partition in bytes""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition', 'FileItem']} })


class FileItem(ConfiguredBaseModel):
    """
    Represents a file or directory item found on a partition
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe'})

    id: str = Field(default=..., description="""Unique identifier for this file item record""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem']} })
    drive_uuid: str = Field(default=..., description="""UUID of the hard drive where item was found""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'FileItem']} })
    partition_uuid: str = Field(default=..., description="""UUID of the partition where item was found""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'ScanPartition']} })
    path: str = Field(default=..., description="""Full path of the item on the partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem']} })
    size_bytes: int = Field(default=..., description="""Size of the item in bytes""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition', 'FileItem']} })
    hash: str = Field(default=..., description="""Hash of the item contents (e.g., SHA256, MD5)""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'CASIdentity']} })
    hash_algorithm: Optional[str] = Field(default=None, description="""Algorithm used to generate the hash""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem']} })


class CASIdentity(ConfiguredBaseModel):
    """
    Content Addressable Storage identifier consisting of version and hash. Used to uniquely identify content by its cryptographic hash.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe'})

    version: str = Field(default=..., description="""CAS version string (e.g., \"DZ0\")""", json_schema_extra = { "linkml_meta": {'domain_of': ['CASIdentity']} })
    hash: str = Field(default=..., description="""Base58-encoded BLAKE3 hash of the content""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'CASIdentity']} })


class InspectStorage(Command):
    """
    Command to discover and list all hard drives and partitions with details to help identify storage for scanning
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/commands'})

    pass


class ScanPartition(Command):
    """
    Command to scan a specific partition and catalog all files
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/commands'})

    partition_uuid: str = Field(default=..., description="""UUID of the partition to scan""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'ScanPartition']} })


class AssignPartitionMount(Command):
    """
    Command to assign a partition to a mount point, expressing the desired state for where a partition should be mounted
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/commands'})

    partition: Partition = Field(default=..., description="""The partition to be mounted""", json_schema_extra = { "linkml_meta": {'domain_of': ['AssignPartitionMount']} })
    mount_point: str = Field(default=..., description="""The desired mount point path""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'AssignPartitionMount']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Command.model_rebuild()
HardDrive.model_rebuild()
Partition.model_rebuild()
FileItem.model_rebuild()
CASIdentity.model_rebuild()
InspectStorage.model_rebuild()
ScanPartition.model_rebuild()
AssignPartitionMount.model_rebuild()
