#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 12:26:00 2020

@author: piaverous
"""

class Match(object):

    def __init__(self, id, winner_id, loser_id, winner_side, crashed):
        self.id = id
        self.winner_id = winner_id
        self.loser_id = loser_id
        self.winner_side = winner_side
        self.crashed = crashed

    @classmethod
    def from_tuple(cls, tup):
        return cls(*tup)