# Auto generated from feature_schema.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-12-20T14:15:05
# Schema: dizzy-feature-schema
#
# id: https://w3id.org/dizzy/feature-schema
# description: LinkML schema for defining Dizzy features with commands, events, procedures, and policies
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
DIZZY = CurieNamespace('dizzy', 'https://w3id.org/dizzy/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = DIZZY


# Types

# Class references
class CommandName(extended_str):
    pass


class EventName(extended_str):
    pass


class ProcedureName(extended_str):
    pass


class PolicyName(extended_str):
    pass


@dataclass(repr=False)
class Feature(YAMLRoot):
    """
    A complete feature definition with commands, events, procedures, and policies
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DIZZY["Feature"]
    class_class_curie: ClassVar[str] = "dizzy:Feature"
    class_name: ClassVar[str] = "Feature"
    class_model_uri: ClassVar[URIRef] = DIZZY.Feature

    description: str = None
    commands: Optional[Union[dict[Union[str, CommandName], Union[dict, "Command"]], list[Union[dict, "Command"]]]] = empty_dict()
    events: Optional[Union[dict[Union[str, EventName], Union[dict, "Event"]], list[Union[dict, "Event"]]]] = empty_dict()
    procedures: Optional[Union[dict[Union[str, ProcedureName], Union[dict, "Procedure"]], list[Union[dict, "Procedure"]]]] = empty_dict()
    policies: Optional[Union[dict[Union[str, PolicyName], Union[dict, "Policy"]], list[Union[dict, "Policy"]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        self._normalize_inlined_as_dict(slot_name="commands", slot_type=Command, key_name="name", keyed=True)

        self._normalize_inlined_as_dict(slot_name="events", slot_type=Event, key_name="name", keyed=True)

        self._normalize_inlined_as_dict(slot_name="procedures", slot_type=Procedure, key_name="name", keyed=True)

        self._normalize_inlined_as_dict(slot_name="policies", slot_type=Policy, key_name="name", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Command(YAMLRoot):
    """
    A command that can be issued to trigger a procedure
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DIZZY["Command"]
    class_class_curie: ClassVar[str] = "dizzy:Command"
    class_name: ClassVar[str] = "Command"
    class_model_uri: ClassVar[URIRef] = DIZZY.Command

    name: Union[str, CommandName] = None
    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, CommandName):
            self.name = CommandName(self.name)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Event(YAMLRoot):
    """
    An event that can be emitted during execution
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DIZZY["Event"]
    class_class_curie: ClassVar[str] = "dizzy:Event"
    class_name: ClassVar[str] = "Event"
    class_model_uri: ClassVar[URIRef] = DIZZY.Event

    name: Union[str, EventName] = None
    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, EventName):
            self.name = EventName(self.name)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Procedure(YAMLRoot):
    """
    A procedure that executes in response to a command
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DIZZY["Procedure"]
    class_class_curie: ClassVar[str] = "dizzy:Procedure"
    class_name: ClassVar[str] = "Procedure"
    class_model_uri: ClassVar[URIRef] = DIZZY.Procedure

    name: Union[str, ProcedureName] = None
    description: str = None
    command: str = None
    emits: Optional[Union[str, list[str]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, ProcedureName):
            self.name = ProcedureName(self.name)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self._is_empty(self.command):
            self.MissingRequiredField("command")
        if not isinstance(self.command, str):
            self.command = str(self.command)

        if not isinstance(self.emits, list):
            self.emits = [self.emits] if self.emits is not None else []
        self.emits = [v if isinstance(v, str) else str(v) for v in self.emits]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Policy(YAMLRoot):
    """
    A policy that reacts to events and may issue commands
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DIZZY["Policy"]
    class_class_curie: ClassVar[str] = "dizzy:Policy"
    class_name: ClassVar[str] = "Policy"
    class_model_uri: ClassVar[URIRef] = DIZZY.Policy

    name: Union[str, PolicyName] = None
    description: str = None
    event: str = None
    emits: Optional[Union[str, list[str]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, PolicyName):
            self.name = PolicyName(self.name)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self._is_empty(self.event):
            self.MissingRequiredField("event")
        if not isinstance(self.event, str):
            self.event = str(self.event)

        if not isinstance(self.emits, list):
            self.emits = [self.emits] if self.emits is not None else []
        self.emits = [v if isinstance(v, str) else str(v) for v in self.emits]

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.feature__description = Slot(uri=DIZZY.description, name="feature__description", curie=DIZZY.curie('description'),
                   model_uri=DIZZY.feature__description, domain=None, range=str)

slots.feature__commands = Slot(uri=DIZZY.commands, name="feature__commands", curie=DIZZY.curie('commands'),
                   model_uri=DIZZY.feature__commands, domain=None, range=Optional[Union[dict[Union[str, CommandName], Union[dict, Command]], list[Union[dict, Command]]]])

slots.feature__events = Slot(uri=DIZZY.events, name="feature__events", curie=DIZZY.curie('events'),
                   model_uri=DIZZY.feature__events, domain=None, range=Optional[Union[dict[Union[str, EventName], Union[dict, Event]], list[Union[dict, Event]]]])

slots.feature__procedures = Slot(uri=DIZZY.procedures, name="feature__procedures", curie=DIZZY.curie('procedures'),
                   model_uri=DIZZY.feature__procedures, domain=None, range=Optional[Union[dict[Union[str, ProcedureName], Union[dict, Procedure]], list[Union[dict, Procedure]]]])

slots.feature__policies = Slot(uri=DIZZY.policies, name="feature__policies", curie=DIZZY.curie('policies'),
                   model_uri=DIZZY.feature__policies, domain=None, range=Optional[Union[dict[Union[str, PolicyName], Union[dict, Policy]], list[Union[dict, Policy]]]])

slots.command__name = Slot(uri=DIZZY.name, name="command__name", curie=DIZZY.curie('name'),
                   model_uri=DIZZY.command__name, domain=None, range=URIRef)

slots.command__description = Slot(uri=DIZZY.description, name="command__description", curie=DIZZY.curie('description'),
                   model_uri=DIZZY.command__description, domain=None, range=Optional[str])

slots.event__name = Slot(uri=DIZZY.name, name="event__name", curie=DIZZY.curie('name'),
                   model_uri=DIZZY.event__name, domain=None, range=URIRef)

slots.event__description = Slot(uri=DIZZY.description, name="event__description", curie=DIZZY.curie('description'),
                   model_uri=DIZZY.event__description, domain=None, range=Optional[str])

slots.procedure__name = Slot(uri=DIZZY.name, name="procedure__name", curie=DIZZY.curie('name'),
                   model_uri=DIZZY.procedure__name, domain=None, range=URIRef)

slots.procedure__description = Slot(uri=DIZZY.description, name="procedure__description", curie=DIZZY.curie('description'),
                   model_uri=DIZZY.procedure__description, domain=None, range=str)

slots.procedure__command = Slot(uri=DIZZY.command, name="procedure__command", curie=DIZZY.curie('command'),
                   model_uri=DIZZY.procedure__command, domain=None, range=str)

slots.procedure__emits = Slot(uri=DIZZY.emits, name="procedure__emits", curie=DIZZY.curie('emits'),
                   model_uri=DIZZY.procedure__emits, domain=None, range=Optional[Union[str, list[str]]])

slots.policy__name = Slot(uri=DIZZY.name, name="policy__name", curie=DIZZY.curie('name'),
                   model_uri=DIZZY.policy__name, domain=None, range=URIRef)

slots.policy__description = Slot(uri=DIZZY.description, name="policy__description", curie=DIZZY.curie('description'),
                   model_uri=DIZZY.policy__description, domain=None, range=str)

slots.policy__event = Slot(uri=DIZZY.event, name="policy__event", curie=DIZZY.curie('event'),
                   model_uri=DIZZY.policy__event, domain=None, range=str)

slots.policy__emits = Slot(uri=DIZZY.emits, name="policy__emits", curie=DIZZY.curie('emits'),
                   model_uri=DIZZY.policy__emits, domain=None, range=Optional[Union[str, list[str]]])

