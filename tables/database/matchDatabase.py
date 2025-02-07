#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 12:26:00 2020

@author: piaverous
"""

from .models import Match
from psycopg2.extras import execute_values

class MatchDatabase(object):
    def __init__(self, db_conn):
        self.db_connection = db_conn

    """ Insert multiple matches.
    
    Args :
        matches = [(id, winner_id, loser_id, winner_side)] 
            // List of tuples of matches -> (int, int, int, bool) or (int, int, int)
            // NB: if winner_side is not known, leave empty and it will be set to NULL
            // NBB: winner_id and loser_id are FKEYS to algos table, so this will fail 
            // if you have not inserted the algos beforehand
    """
    def insert_many(self, matches):
        if len(matches) == 0:
            return    

        cur = self.db_connection.cursor()
        execute_values(
            cur,
            "INSERT INTO matches (id, winner_id, loser_id, winner_side, date) VALUES %s",
            map(lambda x: x if len(x) == 5 else (x[0], x[1], x[2], None, x[3]), matches)
        )
        self.db_connection.commit()
        cur.close()


    """ Gets all matches in the DB. """
    def find_all(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT * FROM matches m WHERE NOT m.crashed")
        matches = cur.fetchall()
        cur.close()
        return list(map(Match.from_tuple, matches))


    """ Gets all match ids in the DB. """
    def find_all_ids(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM matches m WHERE NOT m.crashed")
        matches = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], matches))

    
    """ Gets all matches played by a given algo. 
    
    Args :
        algo_id // The ID of the algo for whom you wish to see the matches.
    """
    def find_for_algo(self, algo_id):
        cur = self.db_connection.cursor()
        cur.execute("SELECT * FROM matches m WHERE m.winner_id=%s OR m.loser_id=%s AND NOT m.crashed", (algo_id, algo_id))
        matches = cur.fetchall()
        cur.close()
        return list(map(Match.from_tuple, matches))


    """ Gets all matches played by all algos of a given user. 
    
    Arg
        username 
    """
    def find_for_user(self, username):
        cur = self.db_connection.cursor()
        cur.execute("SELECT m.* FROM matches m, algos a WHERE (m.winner_id=a.id OR m.loser_id=a.id) AND a.username=%s AND NOT m.crashed", (username,))
        matches = cur.fetchall()
        cur.close()
        return list(map(Match.from_tuple, matches))


    """ Gets the IDS of all the matches played by a given algo. 
    
    Args :
        algo_id // The ID of the algo for whom you wish to see the matches.
    """
    def find_ids_for_algo(self, algo_id):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id FROM matches m WHERE m.winner_id=%s OR m.loser_id=%s AND NOT m.crashed", (algo_id, algo_id))
        matches = cur.fetchall()
        cur.close()
        return list(map(lambda x: x[0], matches))

    
    """ Updates a match.
    
    Args :
        match // A Match object
    """
    def update_match(self, match):
        cur = self.db_connection.cursor()
        cur.execute(
            "UPDATE matches m SET winner_id=%s, loser_id=%s, winner_side=%s, crashed=%s, date=%s WHERE m.id=%s", 
            (match.winner_id, match.loser_id, match.winner_side, match.crashed, match.date, match.id)
        )
        self.db_connection.commit()
        cur.close()
    
