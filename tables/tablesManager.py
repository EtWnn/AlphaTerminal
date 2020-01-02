#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 13:41:55 2019

this files handles the three tables that are used to store data about terminal users, algos and matches

@author: etiennew
"""

import pandas as pd
import datetime
import pathlib
import argparse
from progress.bar import Bar

try:
    from .terminalAPI import getAlgoIdLeaderBoard,getLastMatches
except ImportError:
    from terminalAPI import getAlgoIdLeaderBoard,getLastMatches


"""
set the path and folders for the tables and raw replays
"""
REPLAYSPATH = '../raw_replays'
USERTABLEPATH = 'pkl/users_table.pkl'
ALGOTABLEPATH = 'pkl/algos_table.pkl'
MATCHETABLEPATH = 'pkl/matches_table.pkl'

"""
getters for the three tables
"""

def getTableFromPath(file_path, table_default)
    table = None
    try:
        table = pd.read_pickle(pathlib.Path(__file__).parent / file_path)
    except FileNotFoundError:
        print(f"Could not find file at {file_path} ! Returning empty DataFrame...")
        table = table_default
    return table

def getUsersTable():
    default = pd.DataFrame(columns = ['name','algos_list']).set_index('name')
    return getTableFromPath(USERTABLEPATH, default)

def getAlgosTable():
    default = pd.DataFrame(columns = ['id','name','user','matches_list']).set_index('id')
    return getTableFromPath(ALGOTABLEPATH, default)
        
def getMatchesTable():
    default = pd.DataFrame(columns = ['id','winner_id','loser_id','winner_side','download_status','has_crashed']).set_index('id')
    return getTableFromPath(MATCHETABLEPATH, default)

"""
setters for the three tables
"""
def setUsersTable(user_table):
    user_table.to_pickle(pathlib.Path(__file__).parent / USERTABLEPATH)

def setAlgosTable(algos_table):
    algos_table.to_pickle(pathlib.Path(__file__).parent / ALGOTABLEPATH)
        
def setMatchesTable(matches_table):
    matches_table.to_pickle(pathlib.Path(__file__).parent / MATCHETABLEPATH)

"""
return the ids of the algos of a user_id
"""
def getAlgosId(user):
    users_table = getUsersTable()
    return users_table.at[user,'algos_list']

"""
return the ids of the matches of a user
"""
def getMatchId(user = None, algo = None):
    users_table = getUsersTable()
    algos_table = getAlgosTable()
    
    algos_list = [algo]
    if(user):
        algos_list = users_table.at[user,'algos_list']
        
    matches_list = []
    for algo_id in algos_list:
        matches_list = matches_list + algos_table.at[algo_id,'matches_list']
    return matches_list

"""
reset the types of the matches table (sometimes it changes fo some dark reasons...)
"""
def resetTableType():
    matches_table = getMatchesTable()
    dtypes = {'winner_id':int,'loser_id':int,'winner_side':int,'download_status':bool,'has_crashed':bool}
    matches_table = matches_table.astype(dtypes)
    setMatchesTable(matches_table)
    
"""
reset the crashed and downloaded boolean on the matches table
"""
def resetMatchesBool():
    matches_table = getMatchesTable()
    matches_table['download_status'] = False
    matches_table['has_crashed'] = False
    setMatchesTable(matches_table)

"""
update the table by scrapping the matches of every encountered algos starting by a list of algos,
limits itself by a min date and a min rating
if starting_ids is not specified, the 10 best algos will be taken from the leaderboard
min_date has to be a string under the format "YYYY-MM-DD"
if min_date is specified then max_days_delta is ignored
"""
def updateTables(starting_ids = None, min_rating = 2000, min_date = None, max_days_delta = 10, verbose = None):
    
    if(starting_ids == None):
        starting_ids = [algo['id'] for algo in getAlgoIdLeaderBoard()]
    if(min_rating == None):
        min_rating = 2000
    if(max_days_delta == None):
        max_days_delta = 10
    
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

    # Initiate a progress bar
    progress = Bar(f"Updating...", max=len(to_update))
    progress.next(0)
    while to_update:
        algo_id = to_update.pop()
        updated_algos.append(algo_id)
        matches = getLastMatches(algo_id)
        updated_tables = [False,False,False]
        
        if(matches):
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
                    
                # Add opponent to list of people to update as well
                opponent = match['winning_algo'] if match['winning_algo']['id'] != algo_id else match['losing_algo']
                date_delta = (datetime.datetime.strptime( opponent['lastMatchmakingAttempt'][:10], '%Y-%m-%d') - min_date).days
                if (not(opponent['id'] in updated_algos or opponent['id'] in to_update) and opponent['rating'] >= min_rating and date_delta>=0):
                    progress.max += 1 # Update Max of the progress bar
                    to_update.append(opponent['id'])

            if(updated_tables[0]):
                setUsersTable(users_table)
            if(updated_tables[1]):
                setAlgosTable(algos_table)
            if(updated_tables[2]):
                setMatchesTable(matches_table)
           
        progress.next()
        counter += 1   
        if(verbose):
            print(counter,'done,',len(to_update),'remaining')
    progress.finish() # End progress bar


if __name__ == "__main__":
    """
    Main script used for CLI.
    Launch with '--help' to access the CLI's help.
    """
    # The parser for the command line arguments
    parser = argparse.ArgumentParser(
        description="Manage tables for users, algos and matches.")
    parser.add_argument('-r', '--reset', required=False, action='store_true',
                        help='reset the crashed and downloaded boolean on the matches table')
    parser.add_argument('-rt', '--resetType', required=False, action='store_true',
                        help='reset the types of the matches table (it can change for dark reasons...)')
        
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='should run with higher verbosity')

    parser.add_argument('-ids', '--startingIds', metavar="<starting_ids>", required=False,
                        help='if starting_ids is not specified, the 10 best algos will be taken from the leaderboard')
    parser.add_argument('-mr', '--minRating', metavar="<min_rating>", required=False,
                        help='minimum rating of algo to look at (default 2000)')
    parser.add_argument('-md', '--minDate', metavar="<min_date>", required=False,
                        help='start date to search for (default today-max_days_delta)')
    parser.add_argument('-mdd', '--maxDaysDelta', metavar="<max_days_delta>", required=False,
                        help='max number of days to look at (default 10)')
    args = parser.parse_args()

    if args.r:
        resetMatchesBool()
        exit()
    if args.rt:
        resetTableType()
        exit()

    updateTables(
        starting_ids=args.ids, 
        min_rating=args.mr,
        min_date=args.md,
        max_days_delta=args.mdd,
        verbose=args.v
    )