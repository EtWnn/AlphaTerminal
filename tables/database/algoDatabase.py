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


    """ Gets a given set of algos by IDs.
    
    Args :
        algo_ids: int[] // A list of algo ids
    returns:
        Algo[] // A list of Algo objects
    """
    def find_all_by_ids(self, algo_ids):
        if len(algo_ids) == 0:
            return

        if not isinstance(algo_ids[0], tuple):
            algo_ids = list(map(lambda x: (x, ), algo_ids))
        
        cur = self.db_connection.cursor()
        execute_values(
            cur, 
            "SELECT * FROM algos a WHERE a.id IN %s", 
            (algo_ids,)
        )
        algos = cur.fetchall()
        cur.close()
        return list(map(Algo.from_tuple, algos))


    """ Gets all algo ids for a given user
    
    Args :
        username // The name of the user whose algos you search
    returns:
        int[] // A list of algo ids
    """
    def find_all_ids_for_user(self, username):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM algos a WHERE a.username=%s", (username,))
        algos = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], algos))

    
    """ Insert multiple algos.
    
    Args :
        algos = [(id, name, username, rating), (101024, "EAGLE_AS1", "Felix", 2307)] // List of tuples of algos
    """
    def insert_many(self, algos):
        if len(algos) == 0:
            return

        algo_ids = list(map(lambda a: a[0], algos))

        algos_in_db = self.find_all_by_ids(algo_ids)
        algos_in_db_ids = list(map(lambda a: a.id, algos_in_db))

        algos_to_add = []
        algos_to_update = []
        seen_ids = set()
        for algo in algos:
            if algo[0] not in seen_ids:
                seen_ids.add(algo[0])
                if algo[0] not in algos_in_db_ids:
                    algos_to_add.append(algo)
                else:
                    algos_to_update.append(algo)

        cur = self.db_connection.cursor()
        execute_values(
            cur,
            "INSERT INTO algos (id, name, username, rating) VALUES %s",
            algos_to_add
        )

        execute_values(
            cur, 
            "UPDATE algos SET rating=up.rating FROM (VALUES %s) as up(id, name, username, rating) WHERE algos.id=up.id",
            algos_to_update
        )
        self.db_connection.commit()
        cur.close()
    

