#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 14:46:30 2019

@author: etiennew
"""


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
        
def outputFormat(spawn):
    return "{}_{}_{}".format(spawn[0],spawn[1], spawn[2]) # "x_y_unit_type"