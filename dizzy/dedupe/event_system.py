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
	def __init__(self, meta_instrumentation = None):
		self.queue = EventQueue()
		self.listeners = {}
		self._meta_es = meta_instrumentation
		
	def register(self, event_type):
		if event_type not in self.listeners:
			self.listeners[event_type] = []
		

	def subscribe(self, event_type, listener: Listener):
		self.register(event_type)
		self.listeners[event_type].append(listener)

	def _on(self, temp):
		if self._meta_es is not None:
			print(temp)

	def next(self):
		event = self.queue.next()
		event_type = type(event)

		for listener in self.listeners[event_type]:
			vq = EventQueue()

			self._on(EventSystem.MetaActivityStarted('started'))
			listener.run(vq, event)
			self._on(EventSystem.MetaActivityEnded('ended'))
			
			for e in vq.items:
				self.queue.emit(e)

	def run(self):
		while not self.queue.empty():
			self.next()

	@dataclass
	class MetaActivityStarted(Event):
		value: str


	@dataclass
	class MetaActivityEnded(Event):
		value: str

#

class MetaListener(Listener):
	def run(self, queue: EventQueue, event: EventSystem.MetaActivityStarted |  EventSystem.MetaActivityEnded):
		print('Meta:', event)

meta_es = EventSystem()
meta_es.subscribe(EventSystem.MetaActivityStarted, MetaListener)

#

@dataclass
class ExampleEvent(Event):
	value: str

class ExampleListener(Listener):
	def run(self, queue: EventQueue, event: ExampleEvent):
		print(event.value)

#
  
# es = EventSystem(meta_instrumentation=meta_es)
# es.subscribe(ExampleEvent, ExampleListener())

# es.queue.emit(ExampleEvent("Hello World!"))

# for e in es.queue.items:
# 	print(e)

# es.run()