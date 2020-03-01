#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 14:40:48 2019

this scripts allows to download matches

@author: etiennew
"""
import os
import json
import threading
from tqdm import tqdm

try:
    from .database import Database
    from .tablesManager import REPLAYSPATH
    from .terminalAPI import getMatchContent
except ImportError:
    from database import Database
    from tablesManager import REPLAYSPATH
    from terminalAPI import getMatchContent

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
check if the folder for the raw replays exist, if not create it
"""
def checkReplayRepo():
    try:
        os.mkdir(REPLAYSPATH)
    except:
        pass
    
"""
See already downloaded matches
"""
def checkForExistingReplays():
    result = []
    for f in os.listdir(REPLAYSPATH):
        if f[0] != '.':
            result.append(int(f.split('.')[0]))
    return result

"""
Downloads a specific match, and add it to the matches table
"""
def handleMatch(match, db, semaphore=None, pbar=None):
    match_content_b = getMatchContent(match.id)
    has_crashed = True
    try:
        if match_content_b:
            frames = [json.loads(c) for c in searchDico(str(match_content_b))]
            if(len(frames)):
                match.crashed = frames[-1]['endStats']['player1']['crashed'] or frames[-1]['endStats']['player2']['crashed']
                has_crashed = match.crashed
                match.winner_side = int(frames[-1]['endStats']['winner'])
                db.matches.update_match(match)
                if not(has_crashed):
                    f = open(f"{REPLAYSPATH}/{match.id}.replay", 'wb')
                    f.write(match_content_b)
                    f.close()
    except Exception as e:
        has_crashed = True
        pbar.write(f"error for match {match.id} : {e}")
    if has_crashed:
        match.crashed = True
        db.matches.update_match(match)
    if semaphore:
        semaphore.release()
    if pbar:
        pbar.update(1)

"""
Download a selection of matches
if matches_ids is not specified, every match for the matches table will be downloaded
"""
def downloadMatchesSelection(matches=None, db=None):
    print('Configuration running, wait please...')
    if not db:
        db = Database()
    checkReplayRepo()

    if not(matches):
        matches = db.matches.find_all()
    existing_replays = checkForExistingReplays()
    matches_to_download = list(filter(lambda m: m.id not in existing_replays, matches))

    estimated_download_size = 1.8 * len(matches_to_download)

    print(f"Warning! You are about to download {len(matches_to_download)} files (estimated size : {estimated_download_size:.1f} Mo)")
    answer = input("Do you wish to continue? (yes/no): ")
    if('y' in answer.lower()):
        semaphore = threading.Semaphore(value=20)
        pbar = tqdm(desc="Downloading...", total=len(matches_to_download), leave=False)
        for idx, match in enumerate(matches_to_download):
            semaphore.acquire()
            t = threading.Thread(
                target=handleMatch,
                args=(match, db, semaphore, pbar)
            )
            t.start()
            if idx == len(matches_to_download)-1:
                t.join()

"""
Download matches for given algos or users (default is Felix Richter)
"""
def downloadMatches(algos=None, users=["F.Richter", "Felix"]):
    db = Database()
    matches = []
    if not algos:
        for user in users:
            matches += db.matches.find_for_user(user)
        print(f"Found {len(matches)} matches for users {''.join([user + ' & ' for user in users])[:-3]}")
        
    else:
        for algo in algos:
            matches += db.matches.find_for_algo(algo)
        print(f"Found {len(matches)} matches for algos {''.join([str(algo) + ', ' for algo in algos])[:-2]}")

    downloadMatchesSelection(matches, db) 

if __name__ == '__main__':
	db = Database()
	downloadMatchesSelection(db=db)

    # downloadMatches([101522, 100750, 100630, 100616, 100768, 100633])
