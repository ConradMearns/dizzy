from datetime import datetime

import duckdb

class Provenance:
    def __init__(self, conn):
        self.conn = conn
        
    # given an input event, determine if we already have the output event

    def get_activity(self, activity_id: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM activities WHERE activity_id = ?;
        ''', (activity_id,))
        row = cursor.fetchone()
        
        return {
            "activity_id": row[0],
            "start_time": datetime.fromisoformat(row[1]),
            "end_time": datetime.fromisoformat(row[2]) if row[2] else None
        } if row else None
    
    # def all_activity(self) -> dict:
    #     self.conn.sql('SELECT * FROM activities;').show()
    
    
# ENTITIES_GENERATED_BUT_NOT_USED = """
# SELECT entity.*
# FROM entity
# JOIN was_generated_by g ON entity.entity_id = g.entity_id 
# LEFT JOIN used u ON entity.entity_id = u.entity_id
# WHERE u.entity_id IS NULL;
# """
