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
     'description': 'LinkML schema for query objects that define inputs and '
                    'outputs for querying drives, partitions, and file items.',
     'id': 'https://example.org/dedupe/queries',
     'imports': ['linkml:types',
                 'events',
                 '../../../pkg/dizzy/src/dizzy/def/queries'],
     'name': 'dedupe-queries-schema',
     'prefixes': {'dedupe': {'prefix_prefix': 'dedupe',
                             'prefix_reference': 'https://example.org/dedupe/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': '/home/conrad/dizzy/app/dedupe/def/queries.yaml',
     'title': 'Dedupe Queries Data Model'} )


class DomainEvent(ConfiguredBaseModel):
    """
    Base class for all domain events - immutable facts about what happened. This is an abstract class that should be extended by concrete event types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/events'})

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
    drive_uuid: str = Field(default=..., description="""UUID of the hard drive containing this partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'FileItem', 'ListPartitionsInput']} })
    label: Optional[str] = Field(default=None, description="""Optional human-readable label for the partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition']} })
    mount_point: Optional[str] = Field(default=None, description="""Optional mount point where partition is mounted""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'PartitionMountAssigned']} })
    size_bytes: Optional[int] = Field(default=None, description="""Total size of the partition in bytes""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition', 'FileItem']} })


class FileItem(ConfiguredBaseModel):
    """
    Represents a file or directory item found on a partition
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe'})

    id: str = Field(default=..., description="""Unique identifier for this file item record""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem']} })
    drive_uuid: str = Field(default=..., description="""UUID of the hard drive where item was found""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'FileItem', 'ListPartitionsInput']} })
    partition_uuid: str = Field(default=..., description="""UUID of the partition where item was found""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'FileItemScanned', 'ListFileItemsInput']} })
    path: str = Field(default=..., description="""Full path of the item on the partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'FileItemScanned']} })
    size_bytes: int = Field(default=..., description="""Size of the item in bytes""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDrive', 'Partition', 'FileItem']} })
    hash: str = Field(default=..., description="""Hash of the item contents (e.g., SHA256, MD5)""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem']} })
    hash_algorithm: Optional[str] = Field(default=None, description="""Algorithm used to generate the hash""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem']} })


class TestMessage(DomainEvent):
    """
    Simple test event with a single message string
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/events'})

    message: str = Field(default=..., description="""The test message content""", json_schema_extra = { "linkml_meta": {'domain_of': ['TestMessage']} })


class HardDriveDetected(DomainEvent):
    """
    Event recording that a hard drive was detected
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/events'})

    hard_drive: str = Field(default=..., description="""The detected hard drive""", json_schema_extra = { "linkml_meta": {'domain_of': ['HardDriveDetected']} })


class PartitionDetected(DomainEvent):
    """
    Event recording that a partition was detected
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/events'})

    partition: str = Field(default=..., description="""The detected partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['PartitionDetected', 'PartitionMountAssigned']} })


class FileItemScanned(DomainEvent):
    """
    Event recording that a file item was scanned
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/events'})

    partition_uuid: str = Field(default=..., description="""UUID of the partition containing this file""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'FileItemScanned', 'ListFileItemsInput']} })
    path: str = Field(default=..., description="""Full path to the file within the partition""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'FileItemScanned']} })
    size: int = Field(default=..., description="""Size of the file in bytes""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItemScanned']} })
    content_hash: str = Field(default=..., description="""Hash of the file contents""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItemScanned']} })


class PartitionMountAssigned(DomainEvent):
    """
    Event recording that a partition has been assigned to a mount point, representing the desired state. This does not guarantee the partition is actually mounted - reconciliation is needed for that.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/events'})

    partition: str = Field(default=..., description="""The partition assigned to be mounted""", json_schema_extra = { "linkml_meta": {'domain_of': ['PartitionDetected', 'PartitionMountAssigned']} })
    mount_point: str = Field(default=..., description="""The desired mount point path""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'PartitionMountAssigned']} })


class QueryInput(ConfiguredBaseModel):
    """
    Base class for all query input parameter objects. This is an abstract class that should be extended by concrete input types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/queries'})

    pass


class Query(ConfiguredBaseModel):
    """
    Base class for all query result objects. This is an abstract class that should be extended by concrete result types.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://example.org/dizzy/queries'})

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

    drives: list[str] = Field(default=..., description="""List of hard drives found""", json_schema_extra = { "linkml_meta": {'domain_of': ['ListHardDrives']} })


class ListPartitionsInput(QueryInput):
    """
    Input parameters for listing partitions
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    drive_uuid: Optional[str] = Field(default=None, description="""UUID of the hard drive to filter by (optional - if not provided, lists all partitions)""", json_schema_extra = { "linkml_meta": {'domain_of': ['Partition', 'FileItem', 'ListPartitionsInput']} })


class ListPartitions(Query):
    """
    Query result containing a list of partitions
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    partitions: list[str] = Field(default=..., description="""List of partitions found""", json_schema_extra = { "linkml_meta": {'domain_of': ['ListPartitions']} })


class ListFileItemsInput(QueryInput):
    """
    Input parameters for listing file items in a partition
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    partition_uuid: str = Field(default=..., description="""UUID of the partition to list files from""", json_schema_extra = { "linkml_meta": {'domain_of': ['FileItem', 'FileItemScanned', 'ListFileItemsInput']} })


class ListFileItems(Query):
    """
    Query result containing a list of file items
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    file_items: list[str] = Field(default=..., description="""List of file items found""", json_schema_extra = { "linkml_meta": {'domain_of': ['ListFileItems']} })


class ChainEntry(ConfiguredBaseModel):
    """
    A single entry from the event chain with metadata
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    event_hash: str = Field(default=..., description="""SHA256 hash of the event""", json_schema_extra = { "linkml_meta": {'domain_of': ['ChainEntry']} })
    event_type: str = Field(default=..., description="""Class name of the event""", json_schema_extra = { "linkml_meta": {'domain_of': ['ChainEntry']} })
    timestamp: datetime  = Field(default=..., description="""When this event was recorded to the chain""", json_schema_extra = { "linkml_meta": {'domain_of': ['ChainEntry']} })
    event: DomainEvent = Field(default=..., description="""The domain event data""", json_schema_extra = { "linkml_meta": {'domain_of': ['ChainEntry']} })


class GetAllEventsInput(QueryInput):
    """
    Input parameters for getting all events from the chain
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    pass


class GetAllEvents(Query):
    """
    Query result containing all events from the chain in order
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    events: list[ChainEntry] = Field(default=..., description="""List of chain entries in sequence order""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetAllEvents', 'GetEventsByTypes']} })


class GetEventsByTypesInput(QueryInput):
    """
    Input parameters for getting events filtered by type
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    event_types: list[str] = Field(default=..., description="""List of event type names to filter by (e.g., [\"TestMessage\", \"FileItemScanned\"])""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetEventsByTypesInput']} })


class GetEventsByTypes(Query):
    """
    Query result containing filtered events from the chain
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/dedupe/queries'})

    events: list[ChainEntry] = Field(default=..., description="""List of chain entries matching the requested types""", json_schema_extra = { "linkml_meta": {'domain_of': ['GetAllEvents', 'GetEventsByTypes']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
DomainEvent.model_rebuild()
HardDrive.model_rebuild()
Partition.model_rebuild()
FileItem.model_rebuild()
TestMessage.model_rebuild()
HardDriveDetected.model_rebuild()
PartitionDetected.model_rebuild()
FileItemScanned.model_rebuild()
PartitionMountAssigned.model_rebuild()
QueryInput.model_rebuild()
Query.model_rebuild()
ListHardDrivesInput.model_rebuild()
ListHardDrives.model_rebuild()
ListPartitionsInput.model_rebuild()
ListPartitions.model_rebuild()
ListFileItemsInput.model_rebuild()
ListFileItems.model_rebuild()
ChainEntry.model_rebuild()
GetAllEventsInput.model_rebuild()
GetAllEvents.model_rebuild()
GetEventsByTypesInput.model_rebuild()
GetEventsByTypes.model_rebuild()
