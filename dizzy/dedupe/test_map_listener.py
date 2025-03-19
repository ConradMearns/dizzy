import random
import pytest
from typing import List

from pydantic.dataclasses import dataclass

from dizzy.command_queue import CommandQueueSystem, CommandQueue, Event, Listener

@dataclass
class InputEvent(Event):
    value: int

@dataclass
class InputListEvent(Event):
    values: List[int]

@dataclass
class OutputEvent(Event):
    value: int

@dataclass
class OutputListEvent(Event):
    values: List[int]

class MultiplyByTwoListener(Listener):
    def run(self, queue: CommandQueue, event: InputEvent):
        queue.emit( OutputEvent( value = event.value * 2 ) )

class MapCollectorWithCompletion(Listener):
    def __init__(self, expected_count, original_queue):
        self.expected_count = expected_count
        self.original_queue = original_queue
        self.values = []
        self.processed_count = 0
        
    def run(self, queue: CommandQueue, event: OutputEvent):
        # Collect the value
        self.values.append(event.value)
        self.processed_count += 1
        
        # Check if we've processed all expected items
        if self.processed_count == self.expected_count:
            # Emit the final output list event with all collected values
            self.original_queue.emit(OutputListEvent(values=self.values))

class MapListener(Listener):
    def __init__(self, delegate_listener):
        self.cqs = CommandQueueSystem()
        self.delegate_listener = delegate_listener
        self.cqs.subscribe(InputEvent, self.delegate_listener)

    def run(self, queue: CommandQueue, event: InputListEvent):
        # Create a collector with completion tracking
        collector = MapCollectorWithCompletion(len(event.values), queue)
        self.cqs.subscribe(OutputEvent, collector)
        
        # Process each input
        for i in event.values:
            self.cqs.queue.emit(InputEvent(value=i))
        
        # Run until all events are processed
        while self.cqs.queue.has_items():
            self.cqs.run_next()

def test_map_with_multiply_by_two():
    system = CommandQueueSystem()
    
    system.subscribe(InputListEvent, MapListener(MultiplyByTwoListener()))
    
    test_values = [1, 2, 3, 4, 5]
    event = InputListEvent(values=test_values)
    
    system.queue.emit(event)
    system.run_next()
    
    assert system.queue.has_items()
    
    result_event = system.queue.next()
    
    assert isinstance(result_event, OutputListEvent)
    
    expected_results = [x * 2 for x in test_values]
    assert result_event.values == expected_results
