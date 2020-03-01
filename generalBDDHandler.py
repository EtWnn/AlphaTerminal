#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 15:44:01 2019

@author: etiennew
"""

import re
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pathlib
from tqdm import tqdm

import generalIOLib
from utils.config import getTiles, CONFIG

def removeAlreadyComputed():
    generalBDDHandler = GeneralBDDHandler()
    already_computed = [a[0] for a in generalBDDHandler.getAlreadyComputed()]
    for match_id in tqdm(already_computed):
        file = rf'raw_replays/{match_id}.replay'
        if os.path.exists(file):
            os.remove(file)

"""
return the remaning stability of a unit on a 255 scale (so it can be stored as uint8)
"""
def convertStability(unit_type, remaining_stability, uint8 = False):
    threshold_numbers = [1,1,1,40,10,40,1]
    if(uint8):
        return int(255 * remaining_stability / ( threshold_numbers[unit_type] * CONFIG['stabilities'][unit_type]))
    else:
        return remaining_stability / ( threshold_numbers[unit_type] * CONFIG['stabilities'][unit_type])

class GeneralBDDHandler:
    
    def __init__(self):
        
        self.bdd_name = "generalIO_v2"
        self.bdd_path = pathlib.Path(__file__).parent / 'datasets' / (self.bdd_name + '.csv')
        
        self.matrixInputs = generalIOLib.MatrixInput()
        self.flatInputsDic = generalIOLib.FlatInputDic()
        
        if not os.path.exists(self.bdd_path):
            with open(self.bdd_path, "w") as f:
                headers = ";".join(["match_id","flipped","units_list"] + self.flatInputsDic.column_names + ["output"]) + "\n"
                f.write(headers)
        
        
    """
    return the tuples(match_id, flipped) already in the bdd
    """
    def getAlreadyComputed(self):
        df = pd.read_csv(self.bdd_path, usecols = ['match_id','flipped'], delimiter = ";")
        return set(zip(df['match_id'],df['flipped']))
    
    """
    add rows to the bdd
    """
    def addRows(self, match_id, flipped, image_units_list, flat_inputs, outputs):
        
        with open(self.bdd_path, "a") as f:
            for units_list, flat_inputs, output in zip(image_units_list, flat_inputs, outputs):
                row = [match_id, flipped, str(units_list)] + flat_inputs + [output]
                row = ";".join(map(str,row)) + "\n"
                f.write(row)
        
    """
    return an image from a units_list
    """
    def getImage(self, image_units_list, uint8 = False):
        dtype = 'float32'
        if uint8:
            dtype = 'uint8'
        image = np.zeros(generalIOLib.MatrixInput().shape, dtype = dtype)
        for x,y,unit_type, stability in image_units_list:
            u,v = generalIOLib.shiftTile(x,y)
            image[u][v][unit_type] += convertStability(unit_type,stability, uint8) #+= is here to stack information units
        return image
    
    """
    fill an image from a units_list
    """
    def fillImage(self, image, image_units_list, uint8 = False):
        dtype = 'float32'
        if uint8:
            dtype = 'uint8'
        for x,y,unit_type, stability in image_units_list:
            u,v = generalIOLib.shiftTile(x,y)
            image[u][v][unit_type] += convertStability(unit_type,stability, uint8) #+= is here to stack information units
    
    """
    return a set of images
    """
    def getImages(self, image_units_lists, uint8 = False):
        total_shape = [len(image_units_lists)] + list(generalIOLib.MatrixInput().shape)
        dtype = 'float32'
        if uint8:
            dtype = 'uint8'
        images = np.zeros(total_shape, dtype = dtype)
        for i,image_units in enumerate(tqdm(image_units_lists)):
            for x,y,unit_type, stability in image_units:
                u,v = generalIOLib.shiftTile(x,y)
                images[i][u][v][unit_type] += convertStability(unit_type,stability, uint8) #+= is here to stack information units
        return images
    
    """
    plot an image
    """
    def plotImage(self, image_units, image_name = "", output = ""):
        image = self.getImages([image_units])[0]
        
        colors = ['blue','orange','green','yellow','red','purple','red']
        names = ['filter','encryptor','destructor','ping','emp','scrambler','removal']
        markers = ['o','o','o','8','X','s','x']
        tiles = getTiles()
        
        fig = plt.figure(figsize = (7,7))
        
        ax1 = fig.add_subplot(1,1,1)
        ax1.scatter([x for x,y in tiles],[y for x,y in tiles], color = 'grey', marker = '.')
        for unit_type in range(7):
            X = []
            Y = []
            for v in range(29):
                for u in range(15):
                    if(image[u][v][unit_type]):
                        x,y = generalIOLib.shiftBackTile(u,v)
                        X.append(x)
                        Y.append(y)
            ax1.scatter(X,Y, color = colors[unit_type], marker = markers[unit_type], label = names[unit_type])   
        

        if(output != ""):
            if(output == "stop"):
                ax1.scatter([25],[8],color = "brown", marker = 'o', label = "stop")
            else:
                unit_type,x,y = output.split('_')
                ax1.scatter([int(x)],[int(y)],color = "brown", marker = 'o', label = output)
        
        if(image_name != ""):
            ax1.set_title(image_name)
            
        ax1.legend()
        
        plt.show()

