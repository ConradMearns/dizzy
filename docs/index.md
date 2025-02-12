# everything all at once (index)

Possible Example Problems

- Datalake / Database Normalization
- AWS Lambda Deployment
- UI Development
- Game??
- Tag-Oriented File Storage

Things to cover:

- [[Command Query Responsability Seperation]]
- DDD
	- Entities and Value Objects
	- Entity ID
- [[#Listeners and Callbacks]]
- [[#Observer Pattern]]
- [[#Event Loop]]
- Event Loops Emitting Events to Event Loops
- Event Sourcing Command Ledger ID -> Entity ID
- Provenance, Fault Tolerance, Queue Rebuilding
- Automatic Magic with Python Types
- Entity Component Systems and Database Normalization
- Event Sourcing and Deterministic Lockstep
- Domain Driven Command Query Event Sourcing Queue

[[#Errata]]

- [[#Listener Liskov Substitution Mypy Problems]] 
- [[#Discuss Semantics of `subscribe`]]

Links

- [Build your own event system in Python](https://dev.to/kuba_szw/build-your-own-event-system-in-python-5hk6)
- [Building Efficient Event-Driven ETL Processes on Google Cloud: Best Practices, Correlation ID Tracking and Testing](https://douwevandermeij.medium.com/building-efficient-event-driven-etl-processes-on-google-cloud-best-practices-correlation-id-2a508b45a39b)
- [Mentat](https://github.com/mozilla/mentat)
- https://www.cosmicpython.com/blog/2017-09-19-why-use-domain-events.html
- https://www.cosmicpython.com/
- https://blog.jannikwempe.com/domain-driven-design-entities-value-objects
- https://ogrady.github.io/jekyll/update/2021/12/17/entity-component-system.html

Links - less relevant

- [Rust's trait system is a proof engine, let's make it prove us an ABI! - Pierre Avital](https://www.youtube.com/watch?v=g6mUtBVESb0)

---

# Listeners and Callbacks

```python
class Listener:
	def __init__(self):
		self.callbacks = []
	
	def add_listener(self, cb):
		self.callbacks.append(cb)

	def fire(self):
		for cb in self.callbacks:
			cb()
```

Example

```python
def on_event():
    print("Event has been fired!")

def on_another_event():
    print("Another event handler called.")

event_listener = Listener()

event_listener.add_listener(on_event)
event_listener.add_listener(on_another_event)

event_listener.fire()
```

# Observer Pattern

```python
class Subject:
	_state: int = None
	_observers: List[Observer] = []
	
	def attach(self, observer: Observer):
		self._observers.append(observer)
	
	def notify(self):
		for observer in self._observers:
			observer.update(self)

class ObserverA:
	def update(self, subject: Subject) -> None:
		print(subject._state)
```

# Event Loop

Instead of 'Subjects' that notify observers, we have an `EventSystem` that passes Events

```python
class EventQueue:
	def __init__(self):
		self.items = []
		
	def emit(self, item):
		self.items.append(item)
	
	def next(self):
		return self.items.pop(0)

class Listener(ABC):
	def run(self, queue: EventQueue, event: Event):
		pass

@dataclass
class ExampleEvent(Event):
	value: str

class EventSystem:
	def __init__(self):
		self.queue = EventQueue()
		
	def register(self, event_type):
		if event_type not in self.listeners
			self.listeners[event_type] = []
	
	def subscribe(self, event_type, listener: Listener):
		self.register(event_type)
		self.listeners[event_type].append(listener)

	def next(self):
		event = self.queue.next()
		event_type = type(event)

		for listener in self.listeners[event_type]:
			listener.run(self.queue, event)
			# or... get into this later?
			vq = EventQueue()
			listener.run(vq, event)
			for e in vq.items:
				self.queue.emit(e)
```

Criticisms:
- Listeners shouldn't have full access to the queue - depending on the implementation a developer may cause damage via empty, or a sort, or a loop

# Event Loops Emitting...

I imagined a pattern like this - but realized now that it's been coded that if `self._on` is something like

```python
def _on(self, event: Event):
	if self._meta_es is not None:
		self._meta_es.queue.emit(event)
```

then doing something like

```python
...
activity_id = self._on(EventSystem.ActivityStarted('started', datetime.now()))
listener.run(vq, event)
self._on(EventSystem.ActivityEnded('ended', activity_id, datetime.now()))
...
```

maybe isn't well supported...

I supposed that ID's could be gleaned from the Event Queue - that when storing into the Event Store we simply auto increment an ID and return it to use as an Entity ID in situations like this. However - the auto-increment is 
1. not a good solution for decentralized distributed systems, 
2. could lead to confusion because `ActivityEnded` would also generate it's own ID and 
3. deeply couples this particular provenance solution to the events being generated
(I may want to strip these `self._on` calls and remove the inner meta `EventSystem` and rely on good-ol-fashion callbacks here)

So what's the alternative here? We have to construct the Activity ID prior to emitting events.
[[I ranted a little bit about why I didn't want to do this]] - but I am feeling now that this was the wrong direction to take.

I suppose the true issue with Entity ID's being passed around manually is one of _permissions_. [[We don't want a user to just pick any arbitrary Entity ID and attach meaningless Events to it ]]- so this issue will need to be revisited.


# Errata
## Listener Liskov Substitution Mypy Problems

Corrected?
```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T', bound=Event)
class Listener(ABC, Generic[T]):
	@abstractmethod
	def run(self, queue, event: T):
		pass

class MyListener(Listener[BuiltRaw]):
	def run(self, queue, event: BuiltRaw):
		pass # ...
```

## Discuss: Semantics of `subscribe`

Typically I have the `subscribe` method take a type, and `Listener` class as parameters. In the `Listener` class is a `run` method which is invoked my the system. Should we instead be using `MyListener.run` instead? That is - should we pass the function pointer directly instead of the class?

I want to lean my answer to whatever is easier to implement in C... I know passing continuations or lambda expressions is probably well supported in Rust, but for whatever reason it feels important to be able to capture the behavior in C also...

I'm still burdened by the enchanting idea of code generation (or, just behind-the-scene execution) of subscriptions based on types. C doesn't have types - so there is no advantage there.