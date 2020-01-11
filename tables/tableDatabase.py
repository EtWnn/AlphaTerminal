import psycopg2
from psycopg2.extras import execute_values

from os import getenv
from dotenv import load_dotenv
load_dotenv()


class Database(object):

    def __init__(self):
        self.conn_string = f"host='{getenv('DB_HOST')}' dbname='{getenv('DB_NAME')}' user='{getenv('DB_USER')}' password='{getenv('DB_PASSWORD')}'"
        self.db_connection = psycopg2.connect(self.conn_string)

    def insert_user(self, user):
        cur = self.db_connection.cursor()
        cur.execute("INSERT INTO users (username) VALUES (%s)", (user,))
        self.db_connection.commit()
        cur.close()

    def insert_users(self, users):
        assert len(users) > 0

        if not isinstance(users[0], tuple):
            users = map(lambda x: (x, ), users)
        cur = self.db_connection.cursor()
        execute_values(
            cur,
            "INSERT INTO users (username) VALUES %s",
            users
        )
        self.db_connection.commit()
        cur.close()

    def insert_algos(self, algos):
        assert len(algos) > 0

        cur = self.db_connection.cursor()
        execute_values(
            cur,
            "INSERT INTO algos (id, name, username) VALUES %s",
            algos
        )
        self.db_connection.commit()
        cur.close()


    def insert_matches(self, matches):
        assert len(matches) > 0

        cur = self.db_connection.cursor()
        execute_values(
            cur,
            "INSERT INTO matches (id, winner_id, loser_id, winner_side) VALUES %s",
            matches
        )
        self.db_connection.commit()
        cur.close()

    def get_registered_users(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], users))
    
    def get_registered_algos_ids(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM algos")
        algos = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], algos))

    def get_match_ids_for_algo(self, algo_id):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM matches m WHERE m.winner_id=%s OR m.loser_id=%s", (algo_id, algo_id))
        matches = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], matches))


if __name__ == "__main__":
    db = Database()
    u = db.get_registered_algos_ids()
    print(u)