# Auto generated from manifest_upload_started.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-12-20T14:24:04
# Schema: dedupe-manifest_upload_started-event
#
# id: https://example.org/dedupe/events/manifest_upload_started
# description: Upload has started for a manifest item
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



class Event(YAMLRoot):
    """
    Base class for all domain events - immutable facts about what happened. This is an abstract class that should be
    extended by concrete event types.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DIZZY["Event"]
    class_class_curie: ClassVar[str] = "dizzy:Event"
    class_name: ClassVar[str] = "Event"
    class_model_uri: ClassVar[URIRef] = DEDUPE.Event


@dataclass(repr=False)
class ManifestUploadStarted(Event):
    """
    Upload has started for a manifest item
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["ManifestUploadStarted"]
    class_class_curie: ClassVar[str] = "dedupe:ManifestUploadStarted"
    class_name: ClassVar[str] = "manifest_upload_started"
    class_model_uri: ClassVar[URIRef] = DEDUPE.ManifestUploadStarted

    event_id: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.event_id):
            self.MissingRequiredField("event_id")
        if not isinstance(self.event_id, str):
            self.event_id = str(self.event_id)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.manifestUploadStarted__event_id = Slot(uri=DEDUPE.event_id, name="manifestUploadStarted__event_id", curie=DEDUPE.curie('event_id'),
                   model_uri=DEDUPE.manifestUploadStarted__event_id, domain=None, range=str)

