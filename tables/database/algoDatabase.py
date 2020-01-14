#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 12:26:00 2020

@author: piaverous
"""

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
    

    """ Gets all IDS of algos in the database. 
    
    returns:
        string[] // A list of IDS 
    """
    def find_all_ids(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM algos")
        algos = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], algos))


    """ Gets all algos for a given user
    
    Args :
        username // The name of the user whose algos you search
    returns:
        Algo[] // A list of algo objects
    """
    def find_all_for_user(self, username):
        cur = self.db_connection.cursor()
        cur.execute("SELECT * FROM algos a WHERE a.username=%s", (username,))
        algos = cur.fetchall()
        cur.close()
        return list(map(Algo.from_tuple, algos))
