# Auto generated from models.yml by pythongen.py version: 0.0.1
# Generation date: 2025-10-25T13:19:46
# Schema: dedupe-schema
#
# id: https://example.org/dedupe
# description: LinkML schema for tracking hard drives, partitions, and filesystem items for deduplication purposes.
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Integer, String

metamodel_version = "1.7.0"
version = None

# Namespaces
DEDUPE = CurieNamespace('dedupe', 'https://example.org/dedupe/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = DEDUPE


# Types

# Class references
class HardDriveUuid(extended_str):
    pass


class PartitionUuid(extended_str):
    pass


class FileItemId(extended_str):
    pass


@dataclass(repr=False)
class HardDrive(YAMLRoot):
    """
    Represents a physical or logical hard drive with a unique identifier
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["HardDrive"]
    class_class_curie: ClassVar[str] = "dedupe:HardDrive"
    class_name: ClassVar[str] = "HardDrive"
    class_model_uri: ClassVar[URIRef] = DEDUPE.HardDrive

    uuid: Union[str, HardDriveUuid] = None
    label: Optional[str] = None
    size_bytes: Optional[int] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.uuid):
            self.MissingRequiredField("uuid")
        if not isinstance(self.uuid, HardDriveUuid):
            self.uuid = HardDriveUuid(self.uuid)

        if self.label is not None and not isinstance(self.label, str):
            self.label = str(self.label)

        if self.size_bytes is not None and not isinstance(self.size_bytes, int):
            self.size_bytes = int(self.size_bytes)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Partition(YAMLRoot):
    """
    Represents a partition on a hard drive
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["Partition"]
    class_class_curie: ClassVar[str] = "dedupe:Partition"
    class_name: ClassVar[str] = "Partition"
    class_model_uri: ClassVar[URIRef] = DEDUPE.Partition

    uuid: Union[str, PartitionUuid] = None
    drive_uuid: str = None
    label: Optional[str] = None
    mount_point: Optional[str] = None
    size_bytes: Optional[int] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.uuid):
            self.MissingRequiredField("uuid")
        if not isinstance(self.uuid, PartitionUuid):
            self.uuid = PartitionUuid(self.uuid)

        if self._is_empty(self.drive_uuid):
            self.MissingRequiredField("drive_uuid")
        if not isinstance(self.drive_uuid, str):
            self.drive_uuid = str(self.drive_uuid)

        if self.label is not None and not isinstance(self.label, str):
            self.label = str(self.label)

        if self.mount_point is not None and not isinstance(self.mount_point, str):
            self.mount_point = str(self.mount_point)

        if self.size_bytes is not None and not isinstance(self.size_bytes, int):
            self.size_bytes = int(self.size_bytes)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FileItem(YAMLRoot):
    """
    Represents a file or directory item found on a partition
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["FileItem"]
    class_class_curie: ClassVar[str] = "dedupe:FileItem"
    class_name: ClassVar[str] = "FileItem"
    class_model_uri: ClassVar[URIRef] = DEDUPE.FileItem

    id: Union[str, FileItemId] = None
    drive_uuid: str = None
    partition_uuid: str = None
    path: str = None
    size_bytes: int = None
    hash: str = None
    hash_algorithm: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, FileItemId):
            self.id = FileItemId(self.id)

        if self._is_empty(self.drive_uuid):
            self.MissingRequiredField("drive_uuid")
        if not isinstance(self.drive_uuid, str):
            self.drive_uuid = str(self.drive_uuid)

        if self._is_empty(self.partition_uuid):
            self.MissingRequiredField("partition_uuid")
        if not isinstance(self.partition_uuid, str):
            self.partition_uuid = str(self.partition_uuid)

        if self._is_empty(self.path):
            self.MissingRequiredField("path")
        if not isinstance(self.path, str):
            self.path = str(self.path)

        if self._is_empty(self.size_bytes):
            self.MissingRequiredField("size_bytes")
        if not isinstance(self.size_bytes, int):
            self.size_bytes = int(self.size_bytes)

        if self._is_empty(self.hash):
            self.MissingRequiredField("hash")
        if not isinstance(self.hash, str):
            self.hash = str(self.hash)

        if self.hash_algorithm is not None and not isinstance(self.hash_algorithm, str):
            self.hash_algorithm = str(self.hash_algorithm)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.hardDrive__uuid = Slot(uri=DEDUPE.uuid, name="hardDrive__uuid", curie=DEDUPE.curie('uuid'),
                   model_uri=DEDUPE.hardDrive__uuid, domain=None, range=URIRef)

slots.hardDrive__label = Slot(uri=DEDUPE.label, name="hardDrive__label", curie=DEDUPE.curie('label'),
                   model_uri=DEDUPE.hardDrive__label, domain=None, range=Optional[str])

slots.hardDrive__size_bytes = Slot(uri=DEDUPE.size_bytes, name="hardDrive__size_bytes", curie=DEDUPE.curie('size_bytes'),
                   model_uri=DEDUPE.hardDrive__size_bytes, domain=None, range=Optional[int])

slots.partition__uuid = Slot(uri=DEDUPE.uuid, name="partition__uuid", curie=DEDUPE.curie('uuid'),
                   model_uri=DEDUPE.partition__uuid, domain=None, range=URIRef)

slots.partition__drive_uuid = Slot(uri=DEDUPE.drive_uuid, name="partition__drive_uuid", curie=DEDUPE.curie('drive_uuid'),
                   model_uri=DEDUPE.partition__drive_uuid, domain=None, range=str)

slots.partition__label = Slot(uri=DEDUPE.label, name="partition__label", curie=DEDUPE.curie('label'),
                   model_uri=DEDUPE.partition__label, domain=None, range=Optional[str])

slots.partition__mount_point = Slot(uri=DEDUPE.mount_point, name="partition__mount_point", curie=DEDUPE.curie('mount_point'),
                   model_uri=DEDUPE.partition__mount_point, domain=None, range=Optional[str])

slots.partition__size_bytes = Slot(uri=DEDUPE.size_bytes, name="partition__size_bytes", curie=DEDUPE.curie('size_bytes'),
                   model_uri=DEDUPE.partition__size_bytes, domain=None, range=Optional[int])

slots.fileItem__id = Slot(uri=DEDUPE.id, name="fileItem__id", curie=DEDUPE.curie('id'),
                   model_uri=DEDUPE.fileItem__id, domain=None, range=URIRef)

slots.fileItem__drive_uuid = Slot(uri=DEDUPE.drive_uuid, name="fileItem__drive_uuid", curie=DEDUPE.curie('drive_uuid'),
                   model_uri=DEDUPE.fileItem__drive_uuid, domain=None, range=str)

slots.fileItem__partition_uuid = Slot(uri=DEDUPE.partition_uuid, name="fileItem__partition_uuid", curie=DEDUPE.curie('partition_uuid'),
                   model_uri=DEDUPE.fileItem__partition_uuid, domain=None, range=str)

slots.fileItem__path = Slot(uri=DEDUPE.path, name="fileItem__path", curie=DEDUPE.curie('path'),
                   model_uri=DEDUPE.fileItem__path, domain=None, range=str)

slots.fileItem__size_bytes = Slot(uri=DEDUPE.size_bytes, name="fileItem__size_bytes", curie=DEDUPE.curie('size_bytes'),
                   model_uri=DEDUPE.fileItem__size_bytes, domain=None, range=int)

slots.fileItem__hash = Slot(uri=DEDUPE.hash, name="fileItem__hash", curie=DEDUPE.curie('hash'),
                   model_uri=DEDUPE.fileItem__hash, domain=None, range=str)

slots.fileItem__hash_algorithm = Slot(uri=DEDUPE.hash_algorithm, name="fileItem__hash_algorithm", curie=DEDUPE.curie('hash_algorithm'),
                   model_uri=DEDUPE.fileItem__hash_algorithm, domain=None, range=Optional[str])

