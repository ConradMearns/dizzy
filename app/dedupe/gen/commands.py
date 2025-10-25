# Auto generated from commands.yml by pythongen.py version: 0.0.1
# Generation date: 2025-10-25T15:01:52
# Schema: dedupe-commands-schema
#
# id: https://example.org/dedupe/commands
# description: LinkML schema for command objects that represent operations to be performed on drives and partitions.
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



class Command(YAMLRoot):
    """
    Base class for all commands that can be executed in the dedupe system
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["Command"]
    class_class_curie: ClassVar[str] = "dedupe:Command"
    class_name: ClassVar[str] = "Command"
    class_model_uri: ClassVar[URIRef] = DEDUPE.Command


@dataclass(repr=False)
class ScanPartition(Command):
    """
    Command to scan a specific partition and catalog all files
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["ScanPartition"]
    class_class_curie: ClassVar[str] = "dedupe:ScanPartition"
    class_name: ClassVar[str] = "ScanPartition"
    class_model_uri: ClassVar[URIRef] = DEDUPE.ScanPartition

    partition_uuid: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.partition_uuid):
            self.MissingRequiredField("partition_uuid")
        if not isinstance(self.partition_uuid, str):
            self.partition_uuid = str(self.partition_uuid)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.scanPartition__partition_uuid = Slot(uri=DEDUPE.partition_uuid, name="scanPartition__partition_uuid", curie=DEDUPE.curie('partition_uuid'),
                   model_uri=DEDUPE.scanPartition__partition_uuid, domain=None, range=str)

