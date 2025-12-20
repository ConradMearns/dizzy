# Auto generated from start_scan.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-12-20T13:02:31
# Schema: dedupe-start_scan-command
#
# id: https://example.org/dedupe/commands/start_scan
# description: Initiates partition scan to discover files
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
DIZZY = CurieNamespace('dizzy', 'https://example.org/dizzy/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = DEDUPE


# Types

# Class references



class Command(YAMLRoot):
    """
    Base class for all commands that can be executed. This is an abstract class that should be extended by concrete
    command types.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DIZZY["Command"]
    class_class_curie: ClassVar[str] = "dizzy:Command"
    class_name: ClassVar[str] = "Command"
    class_model_uri: ClassVar[URIRef] = DEDUPE.Command


@dataclass(repr=False)
class StartScan(Command):
    """
    Initiates partition scan to discover files
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["StartScan"]
    class_class_curie: ClassVar[str] = "dedupe:StartScan"
    class_name: ClassVar[str] = "start_scan"
    class_model_uri: ClassVar[URIRef] = DEDUPE.StartScan

    path: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.path):
            self.MissingRequiredField("path")
        if not isinstance(self.path, str):
            self.path = str(self.path)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.startScan__path = Slot(uri=DEDUPE.path, name="startScan__path", curie=DEDUPE.curie('path'),
                   model_uri=DEDUPE.startScan__path, domain=None, range=str)

