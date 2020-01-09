#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 13:32:09 2019

@author: etienne
"""

CONFIG = {
        'stabilities':[60,30,75,15,5,40,999],
        'cost':[1,4,6,1,3,1],
        'names':['filter','encryptor','destructor','ping','EMP','scrambler','removal']
        }

"""
return all tiles of the board
"""
def getTiles():
    tiles = []
    for x in range(0,14):
        for y in range(0,x+1):
            i = x
            j = 13 - y
            tiles.append([i,j])
            
            i = 27 - x
            j = 13 - y
            tiles.append([i,j])
            
            i = x
            j = 14 + y
            tiles.append([i,j])
            
            i = 27 - x
            j = 14 + y
            tiles.append([i,j])
    return tiles