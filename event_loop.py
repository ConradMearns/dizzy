from abc import ABC
from dataclasses import dataclass

@dataclass
class Event:
	pass

class EventQueue:
	def __init__(self):
		self.items = []
		
	def emit(self, item):
		self.items.append(item)
	
	def next(self):
		return self.items.pop(0)
	
	def empty(self):
		return len(self.items) == 0

class Listener(ABC):
	def run(self, queue: EventQueue, event: Event):
		raise NotImplemented()
	
class EventSystem:
	def __init__(self):
		self.queue = EventQueue()
		self.listeners = {}
		
	def subscribe(self, event_type, listener: Listener):
		if event_type not in self.listeners:
			self.listeners[event_type] = []

		self.listeners[event_type].append(listener)

	def next(self):
		event = self.queue.next()
		event_type = type(event)

		for listener in self.listeners[event_type]:
			listener.run(self.queue, event)

	def run(self):
		while not self.queue.empty():
			self.next()
#

@dataclass
class ExampleEvent(Event):
	value: str

class ExampleListener(Listener):
	def run(self, queue: EventQueue, event: ExampleEvent):
		print(event.value)

#
  
es = EventSystem()
es.subscribe(ExampleEvent, ExampleListener())

es.queue.emit(ExampleEvent("Hello World!"))

for e in es.queue.items:
	print(e)

es.run()