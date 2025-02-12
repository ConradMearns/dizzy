import duckdb

class DuckDBEventStore:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = duckdb.connect(db_path)
        self._initialize_table()

    def initialize_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                data TEXT NOT NULL
            );
        ''')

    def store_event(self, event):
        event_type = type(event).__name__
        event_data = event.to_json()
        self.conn.execute('''
        INSERT INTO events (type, data) VALUE (?, ?);
        ''', (event_type, event_data))
        event_id = self.conn.fetchone()[0]
        return event_id