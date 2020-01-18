#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 13:24:37 2019

@author: etiennew
"""

import requests
import json
import urllib3
import pathlib
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    with open(pathlib.Path(__file__).parent / "credentials") as f:
        credentials = json.load(f)
except FileNotFoundError:
    tqdm.write("please fill the credentials file and reload this script")
    with open(pathlib.Path(__file__).parent / "credentials",'w') as f:
        f.write('{\n\t"username":"",\n\t"password":""\n}\n')
    
"""
return the list of ids od the algos on the leaderboard, from strat_page to end_page (excluded)
there are ten ids by page
"""
def getAlgoIdLeaderBoard(start_page = 1,end_page = 2):
    url = 'https://terminal.c1games.com/api/game/leaderboard?page='
    auth=(credentials['username'], credentials['password'])
    algo_ids = []
    for i in range(start_page,end_page):
        r = requests.get(url+str(i),auth=auth,verify=False)
        content = None
        if (r.status_code == 200):
            content = json.loads(r.content)
            algos = content['data']['algos']
            for a in algos:
                algo_ids.append({k:a[k] for k in ['id','rating','name','user']})
        else:
            tqdm.write('connection error',r.status_code,'for page',i)
    return algo_ids


"""
return a list of dictionnary, each dictionnary is the desciption a match
at best, it will return the 100 last matches of an algo
"""
def getLastMatches(algo_id):
    url = 'https://terminal.c1games.com/api/game/algo/' + str(algo_id) + '/matches'
    auth=(credentials['username'], credentials['password'])
    r = requests.get(url,auth=auth,verify=False)
    if (r.status_code == 200):
        content = json.loads(r.content)
        return content['data']['matches']
    else:
        tqdm.write('connection error',r.status_code,'for algo',algo_id, 'url', url)


"""
return the info on an algo using getLastMatches
"""
def getAlgoInfo(algo_id):
    matches = getLastMatches(algo_id)
    if len(matches) == 0:
        raise ValueError(f"No matches for algo {algo_id}")
    last_match = matches[0]
    algo = last_match['winning_algo'] if last_match['winning_algo']['id'] == algo_id else last_match['losing_algo']
    return (algo_id, algo['name'], algo['user'], algo['rating'])
        

"""
return the raw content (string) of a match from the api
"""
def getMatchContent(match_id):
    try:
        url = 'https://terminal.c1games.com/api/game/replayexpanded/' + str(match_id)
        auth=(credentials['username'], credentials['password'])
        r = requests.get(url,auth=auth,verify=False)
        content = r.content
        return content
    except Exception as e:
        tqdm.write("\nerror trying to download match",match_id,":",e)
    return None

