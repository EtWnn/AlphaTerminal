#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 15:06:18 2019

@author: etiennew
"""

import os
import json
import pathlib

try:
    from .flip_replay import flip_content
except ImportError:
    from flip_replay import flip_content
    

"""
translate the string replay to a readable json format
"""
def searchDico(string):
    index = []
    start_dico = 0
    n_open = 0
    n_close = 0
    l = len(string)
    i = 0
    while(i<l):
        if (string[i] == '{'):
            if(n_open == 0):
                start_dico = i
            n_open += 1
        elif (string[i] == '}'):
            n_close += 1
        if(n_open == n_close and n_open != 0):
            index.append([start_dico,i + 1])
            n_open = 0
            n_close = 0
        i += 1
    if (n_open != n_close):
        print('error: a dico has not been closed')
        return None
    return [string[o:c] for o,c in index]

"""
fetch the replay file and return the string content
"""
def getMatchContent(match_id, flip = False):
    file_path = pathlib.Path(__file__).parent.parent / 'raw_replays/{}.replay'.format(match_id)
    with open(file_path) as f:
        content = f.read()
    if flip:
        return flip_content(content)
    return content


"""
fetch the replay file and return the corresponding match frames
"""
def getMatchFrames(match_id, flip = False):
    content = getMatchContent(match_id, flip)
    content_dicts = searchDico(content)
    return [json.loads(c) for c in content_dicts]

"""
check if one of the players crashed during a game
"""
def hasACrasher(match_frames):
    if (match_frames[-1]['endStats']['player1']['crashed'] == True or match_frames[-1]['endStats']['player2']['crashed'] == True):
        return True
    return False

"""
return the match_ids of the downloaded matches by scanning the raw_replays folder
"""
def getDownloadedMatchIds():
    file_list = os.listdir(pathlib.Path(__file__).parent.parent / 'raw_replays/')
    id_list = []
    for f in file_list:
        id_list.append(int(f.split('.replay')[0]))
    return id_list