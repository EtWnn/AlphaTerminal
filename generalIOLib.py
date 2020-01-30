#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 14:46:30 2019

@author: etiennew
"""

import numpy as np
from utils.config import CONFIG

"""
Retourne les cases utilisables du plateau
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

"""
retourne si la case est sur un board du joueur 1
"""
def isOnEdge(x,y):
    return (x + y == 13) or (x - y == 14)


"""
rotation transformation, (diamond shape board to rectangle shape)
"""
def shiftTile(x,y):
    
    if (x+y)%2:
        return (13 - (y - x))//2,  x+y-13
    else:
        return (13 - (y - 1 -x)) // 2, x + y - 13
    
def shiftBackTile(u,v):
    if v%2:
        return (2*u+v)//2, (v - 2*u + 26)//2 + 1
    else:
        return (2*u+v)//2, (v - 2*u + 26)//2


"""
description of the cnn inputs
"""
class MatrixInput:
    def __init__(self):
        self.shape = (15,29,7)
        
"""
description of the flat inputs
"""
class FlatInputDic:
    def __init__(self):
        self.index = 0
        self.column_names = []
        self.dic = {}
            
        #stats 
        for player in ['p1','p2']:
            for s in ['health','cores','bits']:
                self.append("{}_{}".format(player,s))
        self.append('turn')      
        
    
    def append(self, feature_name):
        self.column_names.append(feature_name)
        self.dic[feature_name] = self.index
        self.index += 1

"""
description of the general outputs
"""
class GeneralOutputLib:
    def __init__(self, eagle_algos = []):
        
        self.column_names = []
        self.dic = {}
        self.index = 0
        
        for x,y in getTiles():
            if(y < 14):
                for unit_type in range(3):
                    self.append("{}_{}_{}".format(x,y,unit_type))
                if isOnEdge(x,y):
                    for unit_type in range(3,6):
                        self.append("{}_{}_{}".format(x,y,unit_type))
                self.append("{}_{}_{}".format(x,y,6))
            
        self.append("stop")
    
    def append(self, output_name):
        self.column_names.append(output_name)
        self.dic[output_name] = self.index
        self.index += 1
    
    """
    given a string output, return the one hot-encoding vector corresponding
    """
    def constructOutput(self, output_name):
        output_vec = np.zeros(self.index, dtype = 'uint8')
        output_index = self.dic[output_name]
        output_vec[output_index] = 1
        return output_vec
    
    """
    given a string output,fill the one hot-encoding vector corresponding
    """
    def fillOutput(self, output_vec, output_name):
        output_index = self.dic[output_name]
        output_vec[output_index] = 1
        return output_vec
    
    
def outputFormat(spawn):
    return "{}_{}_{}".format(spawn[0],spawn[1], spawn[2]) # "x_y_unit_type"