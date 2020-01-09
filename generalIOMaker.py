#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 14:50:56 2019

@author: etiennew
"""

import numpy as np
from tqdm import tqdm

import generalIOLib
from utils.config import CONFIG
from utils.replay_reading import getMatchFrames
from tables.tablesManager import getMatchesTable, getAlgosId, getMatchId
from generalBDDHandler import GeneralBDDHandler

class GeneralIOMaker:
    
    def __init__(self):
               
        self.flatInputDic = generalIOLib.FlatInputDic()
        self.matrixInput = generalIOLib.MatrixInput()
        
    """    
    return the first inputs of a turn (ide the input for the first placement of a turn)
    """
    def __getInitialInputs(self, placement_frame):
        
        image_units = [(x,y,unit_type,stability) for player in ['p1', 'p2'] for unit_type in range(3) for x,y,stability,u_id in placement_frame[player + 'Units'][unit_type] ]
        
        turn_flats = [placement_frame[player + "Stats"][i] for player in ['p1', 'p2'] for i in range(3)]
        turn_flats.append(int(placement_frame["turnInfo"][1])) #turn number  
        
        return image_units, turn_flats
    
    """
    from the previous inputs, and the next placment, constructs the next inputs
    """
    def __nextInput(self, image_units, turn_flats, spawn):
        x,y,unit_type = spawn
        
        #add the new unit
        image_units.append((x,y,unit_type,CONFIG['stabilities'][unit_type]))
        
        #update ressources
        column_name = "p1_"
        if (unit_type < 3):
            column_name += "cores"
            inputIndex = self.flatInputDic.dic[column_name]
            turn_flats[inputIndex] -= CONFIG['cost'][unit_type]
        elif (unit_type < 6):
            column_name += "bits"
            inputIndex = self.flatInputDic.dic[column_name]
            turn_flats[inputIndex] -= CONFIG['cost'][unit_type]
        
    """
    return the inputs and generic outputs of a match from the player 1 perspective
    """
    def getIOs(self, match_frames):
        image_units_list = []
        flat_inputs = []
        outputs = []
        for num_frame,frame in enumerate(match_frames):
            if('turnInfo' in frame):
                if not("endStats" in frame) and frame['turnInfo'][2] == -1: #placement frame of the turn
                    
                    image_units, turn_flats = self.__getInitialInputs(frame)
                    
                    unit_spawns = [(x,y,unit_type) for (x,y),unit_type,u_id,owner in match_frames[num_frame+1]['events']['spawn'] if owner == 1]
                    
                    for spawn in unit_spawns:
                        
                        image_units_list.append(tuple(image_units))
                        flat_inputs.append(list(turn_flats))
                        outputs.append(generalIOLib.outputFormat(spawn))
                        
                        self.__nextInput(image_units, turn_flats, spawn)
                    
                    image_units_list.append(tuple(image_units))
                    flat_inputs.append(list(turn_flats))
                    outputs.append('stop')
                            
        return image_units_list, flat_inputs, outputs
        
    
    """
    compute the general IO for a list of tuple (match_id, flip)
    """
    def compute(self, to_compute):
        bddHandler = GeneralBDDHandler()
        already_computed = bddHandler.getAlreadyComputed()
        computable = [m for m in to_compute if not(m in already_computed)]
        for match_id, flip in tqdm(computable):
            match_frames = getMatchFrames(match_id, flip)
            image_units_list, flat_inputs, outputs = self.getIOs(match_frames)
            bddHandler.addRows(match_id, flip, image_units_list, flat_inputs, outputs)
            

"""
compute the general IO for the eagle algo serie, if no ids is given, takes all of them
"""
def computeEagle(algo_ids = []):
    eagle_algos = list(np.unique(getAlgosId("F.Richter") + getAlgosId("Felix")))
    if(algo_ids == []):
        algo_ids = eagle_algos
    else:
        algo_ids = [algo_id for algo_id in algo_ids if algo_id in eagle_algos]
    
    match_ids = []
    for algo_id in algo_ids:
        match_ids = match_ids + getMatchId(algo = algo_id)
    
    matches_table = getMatchesTable()
    
    to_compute = []
    for match_id in match_ids:
        winner_id, loser_id, winner_side = matches_table.loc[match_id][['winner_id','loser_id','winner_side']]
        eagle_id = winner_id if winner_id in eagle_algos else loser_id
        try:
            assert(eagle_id in eagle_algos)
        except AssertionError as e:
            print(match_id, winner_id, loser_id, winner_side, eagle_id)
        eagle_side = winner_side if winner_id in eagle_algos else 3 - winner_side
        flip = False
        if eagle_side == 2:
            flip = True
        to_compute.append((match_id, flip))
        
    
    generalIOMaker = GeneralIOMaker()
    generalIOMaker.compute(to_compute)