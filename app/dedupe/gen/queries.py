# Auto generated from queries.yml by pythongen.py version: 0.0.1
# Generation date: 2025-10-25T13:19:48
# Schema: dedupe-queries-schema
#
# id: https://example.org/dedupe/queries
# description: LinkML schema for query objects that define inputs and outputs for querying drives, partitions, and file items.
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

from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"
version = None

# Namespaces
DEDUPE = CurieNamespace('dedupe', 'https://example.org/dedupe/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = DEDUPE


# Types

# Class references



class QueryInput(YAMLRoot):
    """
    Base class for all query input parameter objects
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["QueryInput"]
    class_class_curie: ClassVar[str] = "dedupe:QueryInput"
    class_name: ClassVar[str] = "QueryInput"
    class_model_uri: ClassVar[URIRef] = DEDUPE.QueryInput


class Query(YAMLRoot):
    """
    Base class for all query result objects
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["Query"]
    class_class_curie: ClassVar[str] = "dedupe:Query"
    class_name: ClassVar[str] = "Query"
    class_model_uri: ClassVar[URIRef] = DEDUPE.Query


class ListHardDrivesInput(QueryInput):
    """
    Input parameters for listing all hard drives
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["ListHardDrivesInput"]
    class_class_curie: ClassVar[str] = "dedupe:ListHardDrivesInput"
    class_name: ClassVar[str] = "ListHardDrivesInput"
    class_model_uri: ClassVar[URIRef] = DEDUPE.ListHardDrivesInput


@dataclass(repr=False)
class ListHardDrives(Query):
    """
    Query result containing a list of hard drives
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["ListHardDrives"]
    class_class_curie: ClassVar[str] = "dedupe:ListHardDrives"
    class_name: ClassVar[str] = "ListHardDrives"
    class_model_uri: ClassVar[URIRef] = DEDUPE.ListHardDrives

    drives: Union[str, list[str]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.drives):
            self.MissingRequiredField("drives")
        if not isinstance(self.drives, list):
            self.drives = [self.drives] if self.drives is not None else []
        self.drives = [v if isinstance(v, str) else str(v) for v in self.drives]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ListPartitionsInput(QueryInput):
    """
    Input parameters for listing partitions
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["ListPartitionsInput"]
    class_class_curie: ClassVar[str] = "dedupe:ListPartitionsInput"
    class_name: ClassVar[str] = "ListPartitionsInput"
    class_model_uri: ClassVar[URIRef] = DEDUPE.ListPartitionsInput

    drive_uuid: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.drive_uuid is not None and not isinstance(self.drive_uuid, str):
            self.drive_uuid = str(self.drive_uuid)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ListPartitions(Query):
    """
    Query result containing a list of partitions
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["ListPartitions"]
    class_class_curie: ClassVar[str] = "dedupe:ListPartitions"
    class_name: ClassVar[str] = "ListPartitions"
    class_model_uri: ClassVar[URIRef] = DEDUPE.ListPartitions

    partitions: Union[str, list[str]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.partitions):
            self.MissingRequiredField("partitions")
        if not isinstance(self.partitions, list):
            self.partitions = [self.partitions] if self.partitions is not None else []
        self.partitions = [v if isinstance(v, str) else str(v) for v in self.partitions]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ListFileItemsInput(QueryInput):
    """
    Input parameters for listing file items in a partition
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["ListFileItemsInput"]
    class_class_curie: ClassVar[str] = "dedupe:ListFileItemsInput"
    class_name: ClassVar[str] = "ListFileItemsInput"
    class_model_uri: ClassVar[URIRef] = DEDUPE.ListFileItemsInput

    partition_uuid: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.partition_uuid):
            self.MissingRequiredField("partition_uuid")
        if not isinstance(self.partition_uuid, str):
            self.partition_uuid = str(self.partition_uuid)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ListFileItems(Query):
    """
    Query result containing a list of file items
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["ListFileItems"]
    class_class_curie: ClassVar[str] = "dedupe:ListFileItems"
    class_name: ClassVar[str] = "ListFileItems"
    class_model_uri: ClassVar[URIRef] = DEDUPE.ListFileItems

    file_items: Union[str, list[str]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.file_items):
            self.MissingRequiredField("file_items")
        if not isinstance(self.file_items, list):
            self.file_items = [self.file_items] if self.file_items is not None else []
        self.file_items = [v if isinstance(v, str) else str(v) for v in self.file_items]

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.listHardDrives__drives = Slot(uri=DEDUPE.drives, name="listHardDrives__drives", curie=DEDUPE.curie('drives'),
                   model_uri=DEDUPE.listHardDrives__drives, domain=None, range=Union[str, list[str]])

slots.listPartitionsInput__drive_uuid = Slot(uri=DEDUPE.drive_uuid, name="listPartitionsInput__drive_uuid", curie=DEDUPE.curie('drive_uuid'),
                   model_uri=DEDUPE.listPartitionsInput__drive_uuid, domain=None, range=Optional[str])

slots.listPartitions__partitions = Slot(uri=DEDUPE.partitions, name="listPartitions__partitions", curie=DEDUPE.curie('partitions'),
                   model_uri=DEDUPE.listPartitions__partitions, domain=None, range=Union[str, list[str]])

slots.listFileItemsInput__partition_uuid = Slot(uri=DEDUPE.partition_uuid, name="listFileItemsInput__partition_uuid", curie=DEDUPE.curie('partition_uuid'),
                   model_uri=DEDUPE.listFileItemsInput__partition_uuid, domain=None, range=str)

slots.listFileItems__file_items = Slot(uri=DEDUPE.file_items, name="listFileItems__file_items", curie=DEDUPE.curie('file_items'),
                   model_uri=DEDUPE.listFileItems__file_items, domain=None, range=Union[str, list[str]])

