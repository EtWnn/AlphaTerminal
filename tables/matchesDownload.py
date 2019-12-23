#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 14:40:48 2019

this scripts allows to download matches

@author: etiennew
"""

from tqdm import tqdm
import json

import tablesManager
import terminalAPI

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
Download a selection of matches
if matches_ids is not specified, every match for the matches table will be downloaded
"""
def downloadMatchesSelection(matches_ids = None):
    matches_table = tablesManager.getMatchesTable()
    if not(matches_ids):
        matches_ids = list(matches_table.index)
    downloadable = list(matches_table.loc[(matches_table["download_status"]==False) & (matches_table["has_crashed"]==False)].index)
    to_download = list(set([match_id for match_id in matches_ids if match_id in downloadable]))
    for match_id in tqdm(to_download):
        match_content_b = terminalAPI.getMatchContent(match_id)
        match_content = str(match_content_b)
        has_crashed = True
        try:
            if match_content_b:
                frames = [json.loads(c) for c in searchDico(match_content)]
                if(len(frames)):
                    has_crashed = frames[-1]['endStats']['player1']['crashed'] or frames[-1]['endStats']['player2']['crashed']
                    matches_table.at[match_id,'winner_side'] = int(frames[-1]['endStats']['winner'])
                    if not(has_crashed):
                        f = open(tablesManager.REPLAYSPATH + '/' + str(match_id) + '.replay','wb')
                        f.write(match_content_b)
                        f.close()
                        matches_table.at[match_id,"download_status"] = True
        except Exception as e:
            has_crashed = True
            print('error for match ' + str(match_id) + ' :', e)
        if has_crashed:
            matches_table.at[match_id,"has_crashed"] = True
        tablesManager.setMatchesTable(matches_table)
    print("\ndone")
