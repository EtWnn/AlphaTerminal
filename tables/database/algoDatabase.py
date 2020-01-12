from .models import Algo
from psycopg2.extras import execute_values

class AlgoDatabase(object):
    def __init__(self, db_conn):
        self.db_connection = db_conn

    """ Insert multiple algos.
    
    Args :
        algos = [(id, name, username, rating), (101024, "EAGLE_AS1", "Felix", 2307)] // List of tuples of algos
    """
    def insert_many(self, algos):
        if len(algos) == 0:
            return

        cur = self.db_connection.cursor()
        execute_values(
            cur,
            "INSERT INTO algos (id, name, username, rating) VALUES %s",
            algos
        )
        self.db_connection.commit()
        cur.close()
    

    """ Gets all IDS of algos in the database. """
    def find_all_ids(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM algos")
        algos = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], algos))