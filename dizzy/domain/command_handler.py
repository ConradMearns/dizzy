import duckdb

from tdm.command_queue import CommandQueue, CommandQueueSystem, Event, Listener

class HandleProvenance(Listener):
    '''Base class for provenance events'''
    def __init__(self, conn):
        self.conn = conn
        self._init_db()

    def _init_db(self):
        self.conn.sql('''
            CREATE TABLE IF NOT EXISTS activities (
                activity_id TEXT PRIMARY KEY,
                activity_type TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                data TEXT
            );
            
            CREATE TABLE IF NOT EXISTS was_derived_from (
                entity_id_a TEXT NOT NULL, 
                entity_id_b TEXT NOT NULL, 
                PRIMARY KEY (entity_id_a, entity_id_b)--,
                -- FOREIGN KEY(entity_id_a) REFERENCES entities(entity_id),
                -- FOREIGN KEY(entity_id_b) REFERENCES entities(entity_id)
            );

            CREATE TABLE IF NOT EXISTS was_generated_by (
                entity_id TEXT NOT NULL, 
                activity_id TEXT NOT NULL, 
                PRIMARY KEY (entity_id, activity_id)--,
                -- FOREIGN KEY(entity_id) REFERENCES entities(entity_id),
                -- FOREIGN KEY(activity_id) REFERENCES activities(activity_id)
            );

            CREATE TABLE IF NOT EXISTS used (
                entity_id TEXT NOT NULL, 
                activity_id TEXT NOT NULL, 
                PRIMARY KEY (entity_id, activity_id)--,
                -- FOREIGN KEY(entity_id) REFERENCES entities(entity_id),
                -- FOREIGN KEY(activity_id) REFERENCES activities(activity_id)
            );
            
        ''')

    def run(self, queue: CommandQueue, event: Event):
        pass


class HandleActivityStarted(HandleProvenance):
    def run(self, queue: CommandQueue, event: CommandQueueSystem.ActivityStarted):
        self.conn.execute('''
            INSERT INTO activities (activity_id, activity_type, start_time)
            VALUES (?, ?, ?);
        ''', (str(event.activity_id), event.activity_type, event.start_time))


class HandleActivityEnded(HandleProvenance):
    def run(self, queue: CommandQueue, event: CommandQueueSystem.ActivityEnded):
        self.conn.execute('''
            UPDATE activities 
            SET end_time = ?
            WHERE activity_id = ?;
        ''', (event.end_time, str(event.activity_id)))

class HandleEntityHasJSON(HandleProvenance):
    def run(self, queue: CommandQueue, event: CommandQueueSystem.EntityHasJSON):
        self.conn.execute('''
            INSERT INTO entities (entity_id, entity_type, data)
            VALUES (?, ?, ?);
        ''', (event.entity_id, event.entity_type, event.json))

class HandleActivityCrashed(HandleProvenance):
    def run(self, queue: CommandQueue, event: CommandQueueSystem.ActivityCrashed):
        raise NotImplementedError()
        # self.conn.execute('''  ''', () )

class HandleActivityUsedEntity(HandleProvenance):
    def run(self, queue: CommandQueue, event: CommandQueueSystem.ActivityUsedEntity):
        self.conn.execute('''
            INSERT INTO used (activity_id, entity_id) 
            VALUES (?, ?)
            ON CONFLICT DO NOTHING;
        ''', (event.activity_id, event.entity_id) )

class HandleEntityGeneratedFromActivity(HandleProvenance):
    def run(self, queue: CommandQueue, event: CommandQueueSystem.EntityGeneratedFromActivity):
        self.conn.execute('''
            INSERT INTO was_generated_by (entity_id, activity_id) 
            VALUES (?, ?)
            ON CONFLICT DO NOTHING;
        ''', (event.entity_id, event.activity_id) )

class HandleEntityDerivedFromEntity(HandleProvenance):
    def run(self, queue: CommandQueue, event: CommandQueueSystem.EntityDerivedFromEntity):
        self.conn.execute('''
            INSERT INTO was_derived_from (entity_id_a, entity_id_b)
            VALUES (?, ?)
            ON CONFLICT DO NOTHING;;
        ''', (event.originator_entity_id, event.derived_entity_id) )
