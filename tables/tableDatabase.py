#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 12:26:00 2020

@author: piaverous
"""

import psycopg2
from psycopg2.extras import execute_values

from os import getenv
from dotenv import load_dotenv
load_dotenv()


""" A class that represents our Database. Allows interaction with it using psycopg2. """
class Database(object):

    """ Create a database connection. """
    def __init__(self):
        self.conn_string = f"host='{getenv('DB_HOST')}' dbname='{getenv('DB_NAME')}' user='{getenv('DB_USER')}' password='{getenv('DB_PASSWORD')}'"
        self.db_connection = psycopg2.connect(self.conn_string)

    """ Insert a user.
    
    Args :
        username // The username of the user to insert. His id is generated DB-side.
    """
    def insert_user(self, username):
        cur = self.db_connection.cursor()
        cur.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        self.db_connection.commit()
        cur.close()

    """ Insert multiple users.
    
    Args :
        users = ["username1", "username2"] // List of usernames to insert
    """
    def insert_users(self, users):
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

    """ Insert multiple algos.
    
    Args :
        algos = [(id, name, username, rating), (101024, "EAGLE_AS1", "Felix", 2307)] // List of tuples of algos
    """
    def insert_algos(self, algos):
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


    """ Insert multiple matches.
    
    Args :
        matches = [(id, winner_id, loser_id, winner_side)] 
            // List of tuples of matches -> (int, int, int, bool) or (int, int, int)
            // NB: if winner_side is not known, leave empty and it will be set to NULL
            // NBB: winner_id and loser_id are FKEYS to algos table, so this will fail 
            // if you have not inserted the algos beforehand
    """
    def insert_matches(self, matches):
        if len(matches) == 0:
            return    

        cur = self.db_connection.cursor()
        execute_values(
            cur,
            "INSERT INTO matches (id, winner_id, loser_id, winner_side) VALUES %s",
            map(lambda x: x if len(x) == 4 else (x[0], x[1], x[2], None), matches)
        )
        self.db_connection.commit()
        cur.close()

    """ Gets all usernames of users in database. """
    def get_registered_users(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT username FROM users")
        users = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], users))
    
    """ Gets all IDS of algos in the database. """
    def get_registered_algos_ids(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM algos")
        algos = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], algos))

    """ Gets the IDS of all the matches played by a given algo. 
    
    Args :
        algo_id // The ID of the algo for whom you wish to see the matches.
    """
    def get_match_ids_for_algo(self, algo_id):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM matches m WHERE m.winner_id=%s OR m.loser_id=%s", (algo_id, algo_id))
        matches = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], matches))


if __name__ == "__main__":
    db = Database()
    db.get_registered_users()