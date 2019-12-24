#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 17:01:13 2019

This script search in every downloaded replays the locations used by the eagle algos

@author: etienne
"""

import json
from tqdm import tqdm
import numpy as np

from utils.flip_replay import flip_content
from utils.config import getTiles
from tables.tablesManager import getMatchesTable, getAlgosId, setMatchesTable, getMatchId
import matplotlib.pyplot as plt
import pickle

"""
translate a raw replay (string) into a json-readable format
"""
def searchDico(s):
    index = []
    start_dico = 0
    n_open = 0
    n_close = 0
    l = len(s)
    i = 0
    while(i<l):
        if (s[i] == '{'):
            if(n_open == 0):
                start_dico = i
            n_open += 1
        elif (s[i] == '}'):
            n_close += 1
        if(n_open == n_close and n_open != 0):
            index.append([start_dico,i + 1])
            n_open = 0
            n_close = 0
        i += 1
    if (n_open != n_close):
        print("error: incomplete file")
        return []
    return [s[o:c] for o,c in index]

"""
Check if one of the opponents crashed during the game
"""
def hasACrasher(match_frames):
    if (match_frames[-1]['endStats']['player1']['crashed'] == True or match_frames[-1]['endStats']['player2']['crashed'] == True):
        return True
    return False

"""
return all the spawns locations of the player 1 during a match 
"""
def getSpawns(match_frames):
    spawns = []
    for num_frame,frame in enumerate(match_frames):
        if('turnInfo' in frame):
            if not("endStats" in frame) and frame['turnInfo'][2] == -1: #placement frame of the turn
                spawns = spawns + [(x,y,unit_type) for (x,y),unit_type,u_id,owner in match_frames[num_frame+1]['events']['spawn'] if owner == 1]
    return spawns

"""
return the winner side for a match and if a player crashed
"""
def getWinnerSide(match_id):
    with open('raw_replays/{}.replay'.format(match_id)) as f:
            replay = f.read()
    frames = [json.loads(c) for c in searchDico(replay)]
    if(len(frames)):
        has_crashed = frames[-1]['endStats']['player1']['crashed'] or frames[-1]['endStats']['player2']['crashed']
        winner_side = int(frames[-1]['endStats']['winner'])
        return winner_side, has_crashed
    else:
        return 1, True

"""
main function: return the locations used by each eagle algos in the downloaded raw replays
"""
def getLocationsUsed():
    matches_table = getMatchesTable()
    eagle_algos = list(np.unique(getAlgosId("F.Richter") + getAlgosId("Felix")))
    eagle_matches =  list(np.unique(getMatchId("F.Richter") + getMatchId("Felix")))
    matches_ids = matches_table.loc[matches_table.index.isin(eagle_matches) & matches_table['download_status'] == True].index
    loc_used = {eagle_id:[set() for unit_type in range(7)] for eagle_id in eagle_algos}
    
    for compt,match_id in enumerate(tqdm(matches_ids)):
        winner_id, loser_id, winner_side = matches_table.loc[match_id][['winner_id','loser_id','winner_side']]
        if (winner_side == -1):#uninitialised
            winner_side, has_crashed = getWinnerSide(match_id)
            matches_table.at[match_id, 'winner_side'] = winner_side
            matches_table.at[match_id, 'has_crashed'] = has_crashed
        eagle_id = winner_id if winner_id in eagle_algos else loser_id
        try:
            assert(eagle_id in eagle_algos)
        except AssertionError as e:
            print(match_id, winner_id, loser_id, winner_side, eagle_id)
            raise e
        with open('raw_replays/{}.replay'.format(match_id)) as f:
            replay = f.read()
        eagle_side = winner_side if winner_id in eagle_algos else 3 - winner_side
        if eagle_side == 2:
            replay = flip_content(replay)
        content_dicts = searchDico(replay)
        match_frames = [json.loads(c) for c in content_dicts]
        if not(hasACrasher(match_frames)):
            spawns = getSpawns(match_frames)
            for x,y,unit_type in spawns:
                loc_used[eagle_id][unit_type].add((x,y))
    setMatchesTable(matches_table)
    return loc_used

"""
merge the locations used for several algos
"""
def unifyLocs(eagle_locs, eagle_algos = []):
    if(eagle_algos == []):
        eagle_algos = eagle_locs.keys()
    unified_eagle_locs = [set() for i in range(7)]
    for eagle_id in eagle_algos:
        for i in range(7):
            unified_eagle_locs[i] = unified_eagle_locs[i].union(eagle_locs[eagle_id][i])
    return unified_eagle_locs

"""
save the eagle loc file
"""
def saveEagleLoc(eagle_locs):
    with open('tables/eagle_locs.pkl','wb') as f:
        pickle.dump(eagle_locs,f)
        
"""
load the eagle loc file
"""
def loadEagleLoc(eagle_locs):
    with open('tables/eagle_locs.pkl','rb') as f:
        return pickle.load(f)
        
"""
show a plot of some locations on the boards
"""        
def drawLow(locs,title = None):

    tiles = getTiles()
    
    plt.scatter([x for x,y in tiles],[y for x,y in tiles], color = 'grey')
    plt.scatter([x for x,y in locs],[y for x,y in locs], color = 'blue')
    if(title):
        plt.title(title)
    plt.show() 
