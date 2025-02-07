#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 13:41:55 2019

this files handles the three tables that are used to store data about terminal users, algos and matches

@author: etiennew
"""

import datetime
import argparse
from tqdm import tqdm

try:
    from .terminalAPI import getAlgoIdLeaderBoard,getLastMatches
    from .database import Database
except ImportError:
    from terminalAPI import getAlgoIdLeaderBoard,getLastMatches
    from database import Database


"""
set the path and folders for the tables and raw replays
"""
REPLAYSPATH = '../raw_replays'
USERTABLEPATH = 'pkl/users_table.pkl'
ALGOTABLEPATH = 'pkl/algos_table.pkl'
MATCHETABLEPATH = 'pkl/matches_table.pkl'


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
        
    db = Database()
    
    users_table = db.users.find_all_usernames()
    algos_table = db.algos.find_all_ids()
    
    users_to_add = []
    algos_to_add = []
    matches_to_add = []
    added_match_ids = []

    updated_algos = []
    to_update = list(starting_ids)

    # Initiate a progress bar
    pbar = tqdm(desc="Updating...", total=len(to_update))
    while to_update:
        algo_id = to_update.pop()

        updated_algos.append(algo_id)
        matches = getLastMatches(algo_id)

        if(matches):
            algo = matches[0]['winning_algo'] if matches[0]['winning_algo']['id'] == algo_id else matches[0]['losing_algo']
            user = algo['user']
            #we update the user_table
            if(user not in users_table):
                users_table.append(user)
                users_to_add.append(user)

            #we update the algos_table
            if not(algo_id in algos_table):
                algos_table.append(algo_id)
            algos_to_add.append((algo_id, algo['name'], user, algo['rating']))

            matches_for_algo = db.matches.find_ids_for_algo(algo_id)
            for match in matches:
                match_id = match['id']

                if match_id not in matches_for_algo:
                    if match_id not in added_match_ids:
                        matches_to_add.append((match_id, match['winning_algo']['id'],match['losing_algo']['id'], match['date']))
                        added_match_ids.append(match_id)

                    opponent = match['winning_algo'] if match['winning_algo']['id'] != algo_id else match['losing_algo']
                    date_delta = (datetime.datetime.strptime( opponent['lastMatchmakingAttempt'][:10], '%Y-%m-%d') - min_date).days
                    opponent_id = opponent['id']
                    if (
                        not ( opponent_id in updated_algos or opponent_id in to_update ) 
                        and opponent['rating'] >= min_rating 
                        and date_delta>=0
                    ):
                        pbar.total += 1 # Update Max of the progress bar
                        pbar.update(0)
                        to_update.append(opponent_id)
                    
                    # Register the opponent algo as an algo that exists
                    if not(opponent_id in algos_table or opponent_id in algos_to_add):
                        algos_table.append(opponent_id)
                        algos_to_add.append((opponent_id, opponent['name'], opponent['user'], opponent['rating']))
                    if not(opponent['user'] in users_table or opponent['user'] in users_to_add):
                        users_table.append(opponent['user'])
                        users_to_add.append(opponent['user'])

        pbar.update(1)


    db.users.insert_many(users_to_add)
    db.algos.insert_many(algos_to_add)
    db.matches.insert_many(matches_to_add)
    pbar.close() # End progress bar

    print(f"TOTAL")
    print(f"----------------------")
    print(f"USERS ADDED   -- {len(users_to_add)}")
    print(f"ALGOS ADDED   -- {len(algos_to_add)}")
    print(f"MATCHES ADDED -- {len(matches_to_add)}")


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
                        help='minimum rating of algo to look at (default 2000)', type=int)
    parser.add_argument('-md', '--minDate', metavar="<min_date>", required=False,
                        help='start date to search for (default today-max_days_delta)')
    parser.add_argument('-mdd', '--maxDaysDelta', metavar="<max_days_delta>", required=False,
                        help='max number of days to look at (default 10)', type=int)
    args = parser.parse_args()

    if args.reset:
        resetMatchesBool()
        exit()
    if args.resetType:
        resetTableType()
        exit()

    updateTables(
        starting_ids= args.startingIds, 
        min_rating=args.minRating,
        min_date=args.minDate,
        max_days_delta=args.maxDaysDelta,
        verbose=args.verbose
    )