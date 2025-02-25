class Provenance:
    def __init__(self, conn):
        self.conn = conn 
    
    def get_derivations(self, entity_id: str):
        query = """
        SELECT 
            e2.entity_id AS derived_entity_id,
            e2.data AS derived_entity_data
        FROM 
            was_derived_from wdf
        JOIN 
            entities e2 ON wdf.entity_id_b = e2.entity_id
        WHERE 
            wdf.entity_id_a = ?;
        """

        results = self.conn.execute(query, (entity_id,)).fetchall()

        derived_entities = [
            {"entity_id": row[0], "data": row[1]} for row in results
        ]

        return derived_entities
    
    def get_entities(self, entity_type: str):
        query = """
        SELECT 
            entity_id, entity_type, data
        FROM 
            entities
        WHERE 
            entity_type = ?;
        """

        results = self.conn.execute(query, (entity_type,)).fetchall()

        derived_entities = [
            {"entity_id": row[0], "entity_type": row[1], "data": row[2]} for row in results
        ]

        return derived_entities
    
    def all_entities(self):
        query = """
        SELECT 
            entity_id, entity_type, data
        FROM 
            entities
        ;
        """

        results = self.conn.execute(query).fetchall()

        derived_entities = [
            {"entity_id": row[0], "entity_type": row[1], "data": row[2]} for row in results
        ]

        return derived_entities
    