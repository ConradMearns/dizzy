
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dizzy.dedupe.event_system import Event, EventQueue, EventSystem, Listener

import hashlib


@dataclass
class ItemDiscovered(Event):
    timestamp: str
    path: str

@dataclass
class ItemScanned(Event):
    path: str
    blake2s_digest: str

class ScanItem(Listener):
    def run(self, queue: EventQueue, event: ItemDiscovered):
        with open(event.path, "rb") as f:
            digest = hashlib.file_digest(f, "blake2s")
        queue.emit(ItemScanned(event.path, digest.hexdigest() ))

class Print(Listener):
    def run(self, queue: EventQueue, event: Event):
        from rich import print
        print(event)


system = EventSystem()
system.register(ItemDiscovered)
system.register(ItemScanned)
system.subscribe(ItemDiscovered, ScanItem())

for event_type in system.listeners:
    system.subscribe(event_type, Print())

# cli commands

import typer

app = typer.Typer()

@app.command()
def scan(path: Path):
    path = str(path.absolute())
    event = ItemDiscovered(datetime.now().isoformat(), path)
    system.queue.emit(event)
    system.run()

### great - now need the data model

import duckdb

class DedupeWriterListener(Listener):
    def __init__(self, conn):
        self.conn = conn
        self._create_tables()
    
    def _create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS hashitems (
                blake2s_digest TEXT PRIMARY KEY
            );

            CREATE TABLE IF NOT EXISTS itempath (
                path TEXT PRIMARY KEY,
                blake2s_digest TEXT REFERENCES hashitems(blake2s_digest)
            );
        ''')


class ItemScannedHandler(DedupeWriterListener):
    def run(self, queue: EventQueue, event: ItemScanned):
        self.conn.execute('''
        INSERT INTO hashitems VALUES (?)
        ON CONFLICT DO NOTHING
        ''', (event.blake2s_digest,))

        self.conn.execute('''
        INSERT INTO itempath (path, blake2s_digest)
        VALUES (?, ?)
        ON CONFLICT DO NOTHING
        ''', (event.path, event.blake2s_digest))


db = duckdb.connect('test.db')
system.subscribe(ItemScanned, ItemScannedHandler(db))

# test that we wrote something to the db

# python dizzy/dedupe/dedupe.py pyproject.toml 
@app.command()
def tables():
    db.table('itempath').show()
    db.table('hashitems').show()


# first pass
# - collect information about each file, EXIF, meta, date, paths
# - what hard drive / datasource?
# - file size (good opportunity to try a migration)
# - file type
# - dealing with zips...

# always at end
app()
