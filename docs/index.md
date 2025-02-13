# getting dizzy

> “Start Where You Are. Use What You Have. Do What You Can.” - Arthur Ashe

> "Write drunk, edit sober" -  some drunk who has never editted in their life

We've ranted and rambled enough - let's get to work and test out some code.

There isn't one particular goal with this project, this repository is meant to serve as a piece of living proof of failure and progress.
We are engine building - bootstrapping a patradigm for processing that can survive shifting paradigms, requirements, domains, whim and fancy alike. It is the bastard child of many problems:

- Contract work typically demands a new bespoke system be created every 1-3 years. This is fun - but not sustainable. What if we could carry over the largest least-interesting piece of technology every time to provide a backbone for developing and exploring new paradigms instead of re-inventing the wheel every time?

- Questions of which database are best suited for the user, what UI JS frontend is coolest, what programming language is most likely to provide job stability are tired. _It should not matter_ what of these desicions we make now, because we are more likely to be wrong than right anyway. Therefor - we would be better equipped for these questions if we had an archuitecture that granted us the grace of making these mistakes and correcting them - rather than living with the pain of our ignorance forever.

Besides these burning problems - we also have a general burning desire that we share. _Surely some things could be better_.

The architecture we build here is intended not to be the best - but to be as flexible as possible to the point we know longer care about what's best.

# What the heck is this for

- Running interruptable pipelines that can be resumed later
	- Let me write a quick script that will never be used for production workflows real quick...
- Replacing Jupyter as a scientific processing tool to accelerate TRL
	- DAG's are everywhere and in-memory objects are not to be trusted
- Meta-programming without DSL's or Monkey-patching
	- cool IaC bro, can I have a diagram?
- The MO - Moving Objects
	- hey can you send me those vacation photos of me? thx <3
- ???
	- do u got games on ur phone

# How I'm Writing This Document

There are two primary streams of _new content_ I'm using to quide my hand in writting. Ramblings I've recorded from various sources - transcribed, timestamping, summarized, bulletized, re-ingesticized, mentalized and finally written and this lil table of content below.

> I'm not yet sure if I'll include source rambles - I don't think they matter all that much. I may include them for the hell of it later.

# Content:

- [[#Event Sourcing]]
- [[Command Query Responsability Seperation]]
- DDD
	- Entities and Value Objects
	- Entity ID
- [[#Listeners and Callbacks]]
- [[#Observer Pattern]]
- [[#Event Loop]]
- [[#Delaying Event Loop Effects]]
- [[#Event Loops Emitting Events]]
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

# Event Sourcing 

<!-- 
TODO add diagram showing axis of deltas vs state

Event Sourcing
Command Sourcing
Selective (Partial) Event Sourcing / Dual Writes
Event-Carried State Transfer (ECST)
Log Compaction & Snapshotting Hybrids
CDC with Outbox
Traditional State (CRUD via CDC)

-->


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

Instead of 'Subjects' that notify observers, we have an `EventSystem` that passes `Events` to `Listners`.

The `EventQueue` is used as an abstration on top of a list. 
Note that the the `EventSystem` only provides a method for processing the `next` event,
if the EventQurur were instead built with a construct that is thread-safe,
we could make an event system that is naively parallizable.

```python
class Listener(ABC):
	def run(self, queue: EventQueue, event: Event):
		pass

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
```

Criticisms:
- Listeners shouldn't have full access to the queue - depending on the implementation a developer may cause damage via empty, or a sort, or a loop

# Delaying Event Loop Effects

We may want Event Loops to emit events in a way that allows for more fine grained control.
By ensuring that the `EventQueue` is a proper interface that can be passed into `Listener`,
we can add pre and post processing code that has some knowledge about inputs and outputs. 

```python

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
			vq = EventQueue()
			# pre processing code...
			listener.run(vq, event)
			# post processing code...
			for e in vq.items:
				self.queue.emit(e)
```

# Event Loops Emitting Events

::: dizzy.event_loop_emitting.EventSystem

The addition of `ActivityStarted` and `ActivityEnded` shows how even arbitray classes can have domain events encoded inside;
signifiying that the events are dependendant on this specific implementation.
Though, the implementation just prints the events back out for now

```bash
$ python dizzy/event_loop_emitting.py 
ExampleEvent(value='Hello World!')
EventSystem.MetaActivityStarted(value='started')
Hello World!
EventSystem.MetaActivityEnded(value='ended')
```

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


Pushing ahead,
I went and created a basic command system that consume the raw events
(without storing them into an Event Store)
to explore how this would be problematic.

::: dizzy.domain.event_system.ProvenanceDuckDBQueryModel
::: dizzy.domain.event_system.ProvenanceDuckDBListener
::: dizzy.domain.event_system.HandleStarted
::: dizzy.domain.event_system.HandleEnded

How would it look to have some Activity/Entity Manager thing that can delegate Activity ID's to us?

After doing a bit more research - it appears this is just how things need to be with Event Sourcing.

There are a few possible solutions to Entity ID's that are client-generated to avoid the problem of not being able to use sequential integers.

- Snowflake IDs: timestamp, machine ID, sequence number
- Hash Based ID: still needs something like a timestamp or some pseudorandom element
- UUID / KSUID / ULID


# On Entity IDs in Decentralized Systems

This particular aside will need to be made significantly longer at some point.

In a decentralized system where trust is minimal, it may be the case that some Agents are restricted in terms of what entities can be created or modified. Additionally, it is important to correctly attribute Entities with the Agents that created them so that such permisions can be managed in the first place.

Cryptographic Keys and Signatures could be a solution.

For entities - since the Entity ID must be generated prior to attaching a type or any other events, an Agent could create a new public/private keypair and use this to derive the Entity ID.


# Unsorted

It would be slick if we could define our Events and Entities together

```python
class Provenance:
	# Entities that Exist
	Entity: DomainEntity
	Activity: DomainEntity

	# Value objects?
	...

	# Entity Properties
	Activity.Started
	Activity.Ended

	# Relationships
	Activity used Entity
	Entity was_derived_from Entity
```

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