# Auto generated from mutations.yml by pythongen.py version: 0.0.1
# Generation date: 2025-10-25T15:01:55
# Schema: dedupe-mutations-schema
#
# id: https://example.org/dedupe/mutations
# description: LinkML schema for mutation objects that define inputs and outputs for storing events in the event sourcing system.
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

from linkml_runtime.linkml_model.types import Boolean, Datetime, String
from linkml_runtime.utils.metamodelcore import Bool, XSDDateTime

metamodel_version = "1.7.0"
version = None

# Namespaces
DEDUPE = CurieNamespace('dedupe', 'https://example.org/dedupe/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = DEDUPE


# Types

# Class references



class MutationInput(YAMLRoot):
    """
    Base class for all mutation input parameter objects
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["MutationInput"]
    class_class_curie: ClassVar[str] = "dedupe:MutationInput"
    class_name: ClassVar[str] = "MutationInput"
    class_model_uri: ClassVar[URIRef] = DEDUPE.MutationInput


class Mutation(YAMLRoot):
    """
    Base class for all mutation result objects
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["Mutation"]
    class_class_curie: ClassVar[str] = "dedupe:Mutation"
    class_name: ClassVar[str] = "Mutation"
    class_model_uri: ClassVar[URIRef] = DEDUPE.Mutation


@dataclass(repr=False)
class EventRecordInput(MutationInput):
    """
    Input parameters for storing an event record
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["EventRecordInput"]
    class_class_curie: ClassVar[str] = "dedupe:EventRecordInput"
    class_name: ClassVar[str] = "EventRecordInput"
    class_model_uri: ClassVar[URIRef] = DEDUPE.EventRecordInput

    event_type: str = None
    event_data: str = None
    source: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.event_type):
            self.MissingRequiredField("event_type")
        if not isinstance(self.event_type, str):
            self.event_type = str(self.event_type)

        if self._is_empty(self.event_data):
            self.MissingRequiredField("event_data")
        if not isinstance(self.event_data, str):
            self.event_data = str(self.event_data)

        if self.source is not None and not isinstance(self.source, str):
            self.source = str(self.source)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class EventRecord(Mutation):
    """
    Result of storing an event record, containing the content hash and timestamp
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DEDUPE["EventRecord"]
    class_class_curie: ClassVar[str] = "dedupe:EventRecord"
    class_name: ClassVar[str] = "EventRecord"
    class_model_uri: ClassVar[URIRef] = DEDUPE.EventRecord

    event_hash: str = None
    event_type: str = None
    timestamp: Union[str, XSDDateTime] = None
    was_duplicate: Union[bool, Bool] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.event_hash):
            self.MissingRequiredField("event_hash")
        if not isinstance(self.event_hash, str):
            self.event_hash = str(self.event_hash)

        if self._is_empty(self.event_type):
            self.MissingRequiredField("event_type")
        if not isinstance(self.event_type, str):
            self.event_type = str(self.event_type)

        if self._is_empty(self.timestamp):
            self.MissingRequiredField("timestamp")
        if not isinstance(self.timestamp, XSDDateTime):
            self.timestamp = XSDDateTime(self.timestamp)

        if self._is_empty(self.was_duplicate):
            self.MissingRequiredField("was_duplicate")
        if not isinstance(self.was_duplicate, Bool):
            self.was_duplicate = Bool(self.was_duplicate)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.eventRecordInput__event_type = Slot(uri=DEDUPE.event_type, name="eventRecordInput__event_type", curie=DEDUPE.curie('event_type'),
                   model_uri=DEDUPE.eventRecordInput__event_type, domain=None, range=str)

slots.eventRecordInput__event_data = Slot(uri=DEDUPE.event_data, name="eventRecordInput__event_data", curie=DEDUPE.curie('event_data'),
                   model_uri=DEDUPE.eventRecordInput__event_data, domain=None, range=str)

slots.eventRecordInput__source = Slot(uri=DEDUPE.source, name="eventRecordInput__source", curie=DEDUPE.curie('source'),
                   model_uri=DEDUPE.eventRecordInput__source, domain=None, range=Optional[str])

slots.eventRecord__event_hash = Slot(uri=DEDUPE.event_hash, name="eventRecord__event_hash", curie=DEDUPE.curie('event_hash'),
                   model_uri=DEDUPE.eventRecord__event_hash, domain=None, range=str)

slots.eventRecord__event_type = Slot(uri=DEDUPE.event_type, name="eventRecord__event_type", curie=DEDUPE.curie('event_type'),
                   model_uri=DEDUPE.eventRecord__event_type, domain=None, range=str)

slots.eventRecord__timestamp = Slot(uri=DEDUPE.timestamp, name="eventRecord__timestamp", curie=DEDUPE.curie('timestamp'),
                   model_uri=DEDUPE.eventRecord__timestamp, domain=None, range=Union[str, XSDDateTime])

slots.eventRecord__was_duplicate = Slot(uri=DEDUPE.was_duplicate, name="eventRecord__was_duplicate", curie=DEDUPE.curie('was_duplicate'),
                   model_uri=DEDUPE.eventRecord__was_duplicate, domain=None, range=Union[bool, Bool])

