# from command_queue.provenance import Provenance

####

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from datetime import datetime
import hashlib
from typing import Callable, Dict, List, Type
import uuid



#########


import json
from dataclasses import asdict, fields, is_dataclass
from typing import TypeVar

T = TypeVar("T") # Needed for type inference

class JSONSerializable:
    def to_json(self, include_null=False) -> str:
        return json.dumps(self.to_dict(include_null=include_null))
        
    def to_dict(self, include_null=False):
        return asdict(
            self,
            dict_factory=lambda fields: {
                key: value
                for (key, value) in fields
                if (value is not None or include_null) and (not key.startswith('_'))
            }
        ) # type: ignore

    @classmethod
    def from_json(cls: Type[T], json_text: str): # -> T
        json_dict = json.loads(json_text)
        if not is_dataclass(cls):
            raise ValueError(f"{cls.__name__} must be a dataclass")
        field_names = {field.name for field in fields(cls)}
        kwargs = {
            key: value
            for key, value in json_dict.items()
            if key in field_names
        }
        return cls(**kwargs)
    


###########


@dataclass
class Event(ABC, JSONSerializable):
    # id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    pass

class Listener(ABC):
    @abstractmethod
    def run(self, queue: CommandQueue, event: Event):
        pass
    
    # def hint(self):
    #     type_hints = get_type_hints(self.run)
    #     input_type = type_hints.get('event')
    #     print("Input type using get_type_hints:", input_type)
    
class CommandQueue:
    def __init__(self):
        self.events: List[Event] = []

    def emit(self, event: Event):
        self.events.append(event)
        
    def next(self):
        return self.events.pop(0)
    
    def has_items(self):
        return len(self.events) > 0

class CommandQueueSystem:
    def __init__(
        self, 
        queue = CommandQueue(),
        instrumentation: CommandQueueSystem | None = None,
    ):
        self.queue = queue
        self._instrumentation: CommandQueueSystem | None = instrumentation
        
        self.listeners: Dict[Type, List[Listener]] = {}
        self.registered_events: Dict[str, Type[Event]] = {}
        
        self._policies: List[Callable] = []
        
    def _on(self, event: Event):
        if self._instrumentation is not None:
            self._instrumentation.queue.emit(event)

    def register_event(self, event_type):
        # assert issubclass(event_type, Event) # TODO not working?

        event_name = event_type.__name__
        if event_name not in self.registered_events:
            self.registered_events[event_name] = event_type
            
    def subscribe(self, event_type, listener: Listener):
        # assert issubclass(event_type, Event) # TODO not working?
        
        self.register_event(event_type)
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def get_event_types_for_listener(self, listener_class: type):
        registered_event_types = []
        for event_type, listeners in self.listeners.items():
            for listener in listeners:
                if isinstance(listener, listener_class):
                    registered_event_types.append(event_type)
        return registered_event_types

    def policies(self, policies):
        self._policies = policies

    def run_policies(self):
        for policy in self._policies:
            policy(self.queue.events) # assumes the sort runs in-place
            # self.queue.events = policy(self.queue.events)
            
    def run_next(self):
        if not self.queue.has_items():
            return
        
        event = self.queue.next()
        event_type = type(event)
        
        
        # entity_id = get_or_create.. hash?? value object?
        entity_id = hashlib.blake2s(str(event_type.__name__ + event.to_json()).encode()).hexdigest()
        
        
        # create entity id
        self._on(CommandQueueSystem.EntityHasJSON(entity_id, event_type.__name__, event.to_json()))
        
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                vq = CommandQueue()
                activity_id = str(uuid.uuid4())
                
                self._on(CommandQueueSystem.ActivityStarted(activity_id, datetime.now().isoformat()))
                self._on(CommandQueueSystem.ActivityUsedEntity(activity_id, entity_id))
                
                try:
                    listener.run(vq, event)
                except Exception as err:
                    self._on(CommandQueueSystem.ActivityCrashed.from_exception(activity_id, err))
                    # print(f'ERROR {event_type}', err)
                finally:
                    self._on(CommandQueueSystem.ActivityEnded(activity_id, datetime.now().isoformat()))                    

                for derived in vq.events:
                    self.queue.emit(derived)
                    
                    derived_id = hashlib.blake2s(str(type(derived).__name__ + derived.to_json()).encode()).hexdigest()
                    
                    self._on(CommandQueueSystem.EntityHasJSON(derived_id, type(derived).__name__, derived.to_json()))
                    self._on(CommandQueueSystem.EntityGeneratedFromActivity(entity_id, activity_id))
                    self._on(CommandQueueSystem.EntityDerivedFromEntity(entity_id, derived_id))

        if self._instrumentation is not None:
            while self._instrumentation.queue.has_items():
                self._instrumentation.run_next()
                self._instrumentation.run_policies()


    # Instrumentable events

    @dataclass
    class EntityHasJSON(Event):
        entity_id: str#UUID
        entity_type: str
        json: str
                
    @dataclass
    class ActivityStarted(Event):
        activity_id: str#UUID
        activity_type: str#UUID
        start_time: str#datetime

    @dataclass
    class ActivityEnded(Event):
        activity_id: str#UUID
        end_time: str#datetime
    
    @dataclass
    class ActivityCrashed(Event):
        activity_id: str#UUID
        message: str
        trace_str: str
        
        @staticmethod
        def from_exception(activity_id, err: Exception):
            tbe = traceback.TracebackException.from_exception(err)
            # stack_frames = traceback.extract_stack()
            # tbe.stack.extend(stack_frames)
            trace = ''.join(tbe.format())
            return CommandQueueSystem.ActivityCrashed(
                activity_id = activity_id,
                message = str(err),
                trace_str=trace
            )
    
    @dataclass
    class ActivityUsedEntity(Event):
        activity_id: str#UUID
        entity_id: str#UUID
        
    @dataclass
    class EntityGeneratedFromActivity(Event):
        entity_id: str#UUID
        activity_id: str#UUID
    
    @dataclass
    class EntityDerivedFromEntity(Event):
        originator_entity_id: str#UUID
        derived_entity_id: str#UUID