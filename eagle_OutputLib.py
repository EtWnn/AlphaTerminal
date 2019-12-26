#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 08:28:46 2019

@author: etiennew
"""

from tqdm import tqdm
import numpy as np
from eagle_locs_analysis import loadEagleLoc, unifyLocs

"""
This class constructs the set of outputs strictly needed for a set of eagle algos
If None are specified, takes all of them
"""
class OutputLib:
    
    def __init__(self, eagle_algos = []):
        self.eagle_algos = eagle_algos.copy()
        self.eagle_locs = loadEagleLoc()
        self.eagle_locs = unifyLocs(self.eagle_locs, eagle_algos)
        
        self.column_names = []
        self.dic = {}
        self.index = 0
        
        for unit_type in range(7):
            for x,y in self.eagle_locs[unit_type]:
                output_name = "{}_{}_{}".format(unit_type,x,y)
                self.append(output_name)
        
        self.append("stop")
    
    def append(self, output_name):
        self.column_names.append(output_name)
        self.dic[output_name] = self.index
        self.index += 1
        
    
    """
    given a string output, return the one hot-encoding vector corresponding
    """
    def constructOutputs(self, output_names):
        output_vecs = np.zeros((len(output_names), self.index), dtype = 'uint8')
        for i,output_name in tqdm(enumerate(output_names)):
            output_index = self.dic[output_name]
            output_vecs[i][output_index] = 1
        return output_vecs