# Auto generated from create_image_priority_manifest.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-12-20T14:15:06
# Schema: dedupe-create_image_priority_manifest-command
#
# id: https://example.org/dedupe/commands/create_image_priority_manifest
# description: Creates prioritized manifest for upload
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
class CreateImagePriorityManifest(Command):
    """
    Creates prioritized manifest for upload
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["CreateImagePriorityManifest"]
    class_class_curie: ClassVar[str] = "dedupe:CreateImagePriorityManifest"
    class_name: ClassVar[str] = "create_image_priority_manifest"
    class_model_uri: ClassVar[URIRef] = DEDUPE.CreateImagePriorityManifest

    command_id: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.command_id):
            self.MissingRequiredField("command_id")
        if not isinstance(self.command_id, str):
            self.command_id = str(self.command_id)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.createImagePriorityManifest__command_id = Slot(uri=DEDUPE.command_id, name="createImagePriorityManifest__command_id", curie=DEDUPE.curie('command_id'),
                   model_uri=DEDUPE.createImagePriorityManifest__command_id, domain=None, range=str)

