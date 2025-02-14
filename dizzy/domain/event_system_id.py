from abc import ABC
from dataclasses import dataclass
from datetime import datetime
import uuid
from uuid import UUID

#

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
        self._meta_es: EventSystem = meta_instrumentation
		
    def subscribe(self, event_type, listener: Listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        self.listeners[event_type].append(listener)

    def _on(self, event: Event):
        if self._meta_es is not None:
            self._meta_es.queue.emit(event)

    def next(self):
        event = self.queue.next()
        event_type = type(event)

        for listener in self.listeners[event_type]:
            vq = EventQueue()

            activity_id = uuid.uuid4()

            self._on(EventSystem.ActivityStarted(activity_id, 'started', datetime.now()))
            listener.run(vq, event)
            self._on(EventSystem.ActivityEnded(activity_id, 'ended', datetime.now()))
			
            for e in vq.items:
                self.queue.emit(e)

        if self._meta_es is not None:
            self._meta_es.run()

    def run(self):
        while not self.queue.empty():
            self.next()


    # domain events

    @dataclass
    class ActivityStarted(Event):
        activity_id: UUID
        value: str
        start_time: datetime

    @dataclass
    class ActivityEnded(Event):
        activity_id: UUID
        value: str
        end_time: datetime

import duckdb

# no way to throw errors on un-matched domain events?
class ProvenanceDuckDBQueryModel:
    def __init__(self, conn):
        self.conn = conn

    def get_activity(self, activity_id: UUID) -> dict:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM activities WHERE activity_id = ?
        ''', (activity_id,))
        row = cursor.fetchone()
        return {
            "activity_id": row[0],
            "start_time": datetime.fromisoformat(row[1]),
            "end_time": datetime.fromisoformat(row[2]) if row[2] else None
        } if row else None
    
    def all_activity(self) -> dict:
        self.conn.sql('SELECT * FROM activities;').show()
        

# want to make it easy to connect to everything else

class ProvenanceDuckDBListener(Listener):
    def __init__(self, conn):
        self.conn = conn
        self._init_db()

    def _init_db(self):
        self.conn.sql('''
            CREATE TABLE IF NOT EXISTS activities (
                activity_id TEXT PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP
            )
        ''')

        self.conn.sql("""
            CREATE SEQUENCE IF NOT EXISTS seq_activity_id START 1;
        """)

    def run(self, queue, event):
        pass

class HandleStarted(ProvenanceDuckDBListener):
    def run(self, queue, event: EventSystem.ActivityStarted):
        self.conn.execute('''
            INSERT INTO activities (activity_id, start_time)
            VALUES (?, ?)
        ''', (event.activity_id, event.start_time.isoformat() ))


class HandleEnded(ProvenanceDuckDBListener):
    def run(self, queue, event: EventSystem.ActivityEnded):
        self.conn.execute('''
            UPDATE activities 
            SET end_time = ?
            WHERE activity_id = ?
        ''', (event.end_time.isoformat(), event.activity_id))



#

conn = duckdb.connect(":memory:")


prov_es = EventSystem()
prov_es.subscribe(EventSystem.ActivityStarted, HandleStarted(conn))
prov_es.subscribe(EventSystem.ActivityEnded, HandleEnded(conn))


#

@dataclass
class ExampleEvent(Event):
	value: str

class ExampleListener(Listener):
	def run(self, queue: EventQueue, event: ExampleEvent):
		print(event.value)

#

es = EventSystem(meta_instrumentation=prov_es)

es.subscribe(ExampleEvent, ExampleListener())

es.queue.emit(ExampleEvent("Hello World!"))

for e in es.queue.items:
	print(e)

es.run()


prov_q = ProvenanceDuckDBQueryModel(conn)
prov_q.all_activity()