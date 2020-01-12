#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 12:26:00 2020

@author: piaverous
"""

class User(object):

    def __init__(self, username, id):
        self.id = id
        self.username = username

    @classmethod
    def from_tuple(cls, tup):
        return cls(*tup)