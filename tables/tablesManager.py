#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 13:41:55 2019

this files handles the three tables that are used to store data about terminal users, algos and matches

@author: etiennew
"""


import pandas as pd
import datetime

import terminalAPI


"""
set the path and folders for the tables and raw replays
"""
REPLAYSPATH = '/../raw_replays'
USERTABLEPATH = 'users_table.pkl'
ALGOTABLEPATH = 'algos_table.pkl'
MATCHETABLEPATH = 'matches_table.pkl'

"""
getters for the three tables
"""

def getUsersTable():
    user_table = None
    try:
        user_table = pd.read_pickle(USERTABLEPATH)
    except FileNotFoundError:
        user_table = pd.DataFrame(columns = ['name','algos_list']).set_index('name')
    return user_table

def getAlgosTable():
    algos_table = None
    try:
        algos_table = pd.read_pickle(ALGOTABLEPATH)
    except FileNotFoundError:
        algos_table = pd.DataFrame(columns = ['id','name','user','matches_list']).set_index('id')
    return algos_table
        
def getMatchesTable():
    matches_table = None
    try:
        matches_table = pd.read_pickle(MATCHETABLEPATH)
    except FileNotFoundError:
        matches_table = pd.DataFrame(columns = ['id','winner_id','loser_id','winner_side','download_status','has_crashed']).set_index('id')
    return matches_table

"""
setters for the three tables
"""
def setUsersTable(user_table):
    user_table.to_pickle(USERTABLEPATH)

def setAlgosTable(algos_table):
    algos_table.to_pickle(ALGOTABLEPATH)
        
def setMatchesTable(matches_table):
    matches_table.to_pickle(MATCHETABLEPATH)



"""
update the table by scrapping the matches of every encountered algos starting by a list of algos,
limits itself by a min date and a min rating
if starting_ids is not specified, the 10 best algos will be taken from the leaderboard
min_date has to be a string under the format "YYYY-MM-DD"
if min_date is specified then max_days_delta is ignored
"""
def updateTables(starting_ids = None, min_rating = 2000, min_date = None, max_days_delta = 10, verbose = 1):
    
    if(starting_ids == None):
        starting_ids = [algo['id'] for algo in terminalAPI.getAlgoIdLeaderBoard()]
        
    if(min_date == None):
        min_date = datetime.datetime.now() - datetime.timedelta(days = max_days_delta)
    else:
        min_date = datetime.datetime.strptime(min_date, '%Y-%m-%d')
        
    users_table = getUsersTable()
    algos_table = getAlgosTable()
    matches_table = getMatchesTable()
    
    updated_algos = []
    to_update = list(starting_ids)
    counter = 0
    while to_update:
        algo_id = to_update.pop()
        updated_algos.append(algo_id)
        matches = terminalAPI.getLastMatches(algo_id)
        updated_tables = [False,False,False]
        
        if(len(matches)):
            algo = matches[0]['winning_algo'] if matches[0]['winning_algo']['id'] == algo_id else matches[0]['losing_algo']
            user = algo['user']
            
            
            
            #we update the user_table
            if(user in users_table.index):
                if not(algo_id in users_table.at[user,'algos_list']):
                    users_table.at[user,'algos_list'].append(algo_id)
                    updated_tables[0] = True
            else:
                users_table.at[user] = [[algo_id]]
                updated_tables[0] = True
            
            #we update the algos_table
            if not(algo_id in algos_table.index):
                algos_table.at[algo_id] = [algo['name'], user, []]
                updated_tables[1] = True
            for match in matches:
                match_id = match['id']
                if not(match_id in algos_table.at[algo_id,'matches_list']):
                    algos_table.at[algo_id,'matches_list'].append(match_id)
                    updated_tables[1] = True
                if not(match_id in matches_table.index):
                    matches_table.at[match_id] = [match['winning_algo']['id'],match['losing_algo']['id'],-1,False,False]
                    updated_tables[2] = True
                    
                opponent = match['winning_algo'] if match['winning_algo']['id'] != algo_id else match['losing_algo']
                date_delta = (datetime.datetime.strptime( opponent['lastMatchmakingAttempt'][:10], '%Y-%m-%d') - min_date).days
                if (not(opponent['id'] in updated_algos or opponent['id'] in to_update) and opponent['rating'] >= min_rating and date_delta>=0):
                    to_update.append(opponent['id'])
                    
            
            if(updated_tables[0]):
                setUsersTable(users_table)
            if(updated_tables[1]):
                setAlgosTable(algos_table)
            if(updated_tables[2]):
                setMatchesTable(matches_table)
           
        counter += 1   
        if(verbose):
            print(counter,'done,',len(to_update),'remaining')
        
        