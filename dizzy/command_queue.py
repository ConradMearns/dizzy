from __future__ import annotations
from abc import ABC, abstractmethod

from datetime import datetime
import hashlib
import traceback
from typing import Callable, Dict, List, Type, get_type_hints
import uuid

from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder

import json
from dataclasses import asdict

from rich import print

def dump_json(obj):
    return json.dumps(asdict(obj), default=pydantic_encoder)



@dataclass
class Event(ABC):
    pass

class Listener(ABC):
    # Class variable to store output event types
    output_type_hints = []  # Default to empty list
    
    @abstractmethod
    def run(self, queue: CommandQueue, event: Event):
        pass
    
    def input_type_hint(self):
        type_hints = get_type_hints(self.run)
        input_type = type_hints.get('event')
        return input_type
    
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
        queue = None,
        instrumentation: CommandQueueSystem | None = None,
    ):
        self.queue = queue
        if self.queue is None:
            self.queue = CommandQueue()

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
        entity_id = hashlib.blake2s(str(event_type.__name__ + dump_json(event)).encode()).hexdigest()
        
        
        # create entity id
        self._on(CommandQueueSystem.EntityHasJSON(entity_id, event_type.__name__, dump_json(event)))
        
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                vq = CommandQueue()
                activity_id = str(uuid.uuid4())
                activity_type = type(listener).__name__

                self._on(CommandQueueSystem.ActivityStarted(activity_id, activity_type, datetime.now().isoformat()))
                self._on(CommandQueueSystem.ActivityUsedEntity(activity_id, entity_id))
                
                try:
                    listener.run(vq, event)
                except Exception as err:
                    self._on(CommandQueueSystem.ActivityCrashed.from_exception(activity_id, err))
                    # print(f'ERROR {event_type}-{listener}', err)
                    # print(f'EVENT {event}')
                    # traceback.print_exc()
                finally:
                    self._on(CommandQueueSystem.ActivityEnded(activity_id, datetime.now().isoformat()))                    

                for derived in vq.events:
                    self.queue.emit(derived)
                    
                    derived_id = hashlib.blake2s(str(type(derived).__name__ + dump_json(derived)).encode()).hexdigest()
                    
                    self._on(CommandQueueSystem.EntityHasJSON(derived_id, type(derived).__name__, dump_json(derived)))
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
