# Auto generated from events.yml by pythongen.py version: 0.0.1
# Generation date: 2025-10-25T15:01:54
# Schema: dedupe-events-schema
#
# id: https://example.org/dedupe/events
# description: LinkML schema for domain events that capture immutable facts about what has happened in the system.
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



class DomainEvent(YAMLRoot):
    """
    Base class for all domain events - immutable facts about what happened
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["DomainEvent"]
    class_class_curie: ClassVar[str] = "dedupe:DomainEvent"
    class_name: ClassVar[str] = "DomainEvent"
    class_model_uri: ClassVar[URIRef] = DEDUPE.DomainEvent


@dataclass(repr=False)
class FileItemScanned(DomainEvent):
    """
    Event recording that a file item was scanned
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["FileItemScanned"]
    class_class_curie: ClassVar[str] = "dedupe:FileItemScanned"
    class_name: ClassVar[str] = "FileItemScanned"
    class_model_uri: ClassVar[URIRef] = DEDUPE.FileItemScanned

    partition_uuid: str = None
    path: str = None
    size: int = None
    content_hash: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.partition_uuid):
            self.MissingRequiredField("partition_uuid")
        if not isinstance(self.partition_uuid, str):
            self.partition_uuid = str(self.partition_uuid)

        if self._is_empty(self.path):
            self.MissingRequiredField("path")
        if not isinstance(self.path, str):
            self.path = str(self.path)

        if self._is_empty(self.size):
            self.MissingRequiredField("size")
        if not isinstance(self.size, int):
            self.size = int(self.size)

        if self._is_empty(self.content_hash):
            self.MissingRequiredField("content_hash")
        if not isinstance(self.content_hash, str):
            self.content_hash = str(self.content_hash)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.fileItemScanned__partition_uuid = Slot(uri=DEDUPE.partition_uuid, name="fileItemScanned__partition_uuid", curie=DEDUPE.curie('partition_uuid'),
                   model_uri=DEDUPE.fileItemScanned__partition_uuid, domain=None, range=str)

slots.fileItemScanned__path = Slot(uri=DEDUPE.path, name="fileItemScanned__path", curie=DEDUPE.curie('path'),
                   model_uri=DEDUPE.fileItemScanned__path, domain=None, range=str)

slots.fileItemScanned__size = Slot(uri=DEDUPE.size, name="fileItemScanned__size", curie=DEDUPE.curie('size'),
                   model_uri=DEDUPE.fileItemScanned__size, domain=None, range=int)

slots.fileItemScanned__content_hash = Slot(uri=DEDUPE.content_hash, name="fileItemScanned__content_hash", curie=DEDUPE.curie('content_hash'),
                   model_uri=DEDUPE.fileItemScanned__content_hash, domain=None, range=str)

