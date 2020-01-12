from .models import User
from psycopg2.extras import execute_values

class UserDatabase(object):
    def __init__(self, db_conn):
        self.db_connection = db_conn

    """ Insert a user.
    
    Args :
        username // The username of the user to insert. His id is generated DB-side.
    """
    def insert_one(self, username):
        cur = self.db_connection.cursor()
        cur.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        self.db_connection.commit()
        cur.close()


    """ Insert multiple users.
    
    Args :
        users = ["username1", "username2"] // List of usernames to insert
    """
    def insert_many(self, users):
        if len(users) == 0:
            return

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

    """ Gets all Users in database. """
    def find_all(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        return list(map(User.from_tuple, users))


    """ Gets all usernames of users in database. """
    def find_all_usernames(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT username FROM users")
        users = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], users))
    