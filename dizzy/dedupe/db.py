
import duckdb

from dizzy.command_queue import CommandQueue, Listener
from dizzy.dedupe.events import ItemHashed

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
    def run(self, queue: CommandQueue, event: ItemHashed):
        self.conn.execute('''
        INSERT INTO hashitems VALUES (?)
        ON CONFLICT DO NOTHING
        ''', (event.blake2s_digest,))

        self.conn.execute('''
        INSERT INTO itempath (path, blake2s_digest)
        VALUES (?, ?)
        ON CONFLICT DO NOTHING
        ''', (event.path, event.blake2s_digest))



# db = duckdb.connect('test.db')
# system.subscribe(ItemScanned, ItemScannedHandler(db))



# # python dizzy/dedupe/dedupe.py pyproject.toml 
# @app.command()
# def tables():
#     db.table('itempath').show()
#     db.table('hashitems').show()