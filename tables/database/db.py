#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 12:26:00 2020

@author: piaverous
"""

import psycopg2

from os import getenv
from dotenv import load_dotenv
load_dotenv()

from .matchDatabase import MatchDatabase
from .algoDatabase import AlgoDatabase
from .userDatabase import UserDatabase

""" A class that represents our Database. Allows interaction with it using psycopg2. """
class Database(object):

    """ Create a database connection. """
    def __init__(self):
        self.conn_string = f"host='{getenv('DB_HOST')}' dbname='{getenv('DB_NAME')}' user='{getenv('DB_USER')}' password='{getenv('DB_PASSWORD')}'"
        self.db_connection = psycopg2.connect(self.conn_string)
        self.users = UserDatabase(self.db_connection)
        self.algos = AlgoDatabase(self.db_connection)
        self.matches = MatchDatabase(self.db_connection)
