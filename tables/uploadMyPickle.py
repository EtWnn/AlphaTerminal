import pandas as pd
import pathlib
from tqdm import tqdm

import terminalAPI
from tablesManager import USERTABLEPATH, ALGOTABLEPATH, MATCHETABLEPATH
from database import Database

"""
getters for the three tables
"""
def getTableFromPath(file_path, table_default):
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


if __name__ == "__main__":
    db = Database()

    users_table = getUsersTable()
    algos_table = getAlgosTable()
    matches_table = getMatchesTable()

    known_usernames = db.users.find_all_usernames()
    known_algo_ids = db.algos.find_all_ids()
    known_match_ids = db.matches.find_all_ids()

    users_to_add = []
    algos_to_add = []
    matches_to_add = []
    all_algo_ids = set()

    ubar = tqdm(total=users_table.shape[0], desc="Adding Users...")
    for index, user in users_table.iterrows():
        if user.name not in known_usernames:
            known_usernames.append(algo.name)
            users_to_add.append(user.name)
        ubar.update(1)
    ubar.close()
    
    abar = tqdm(total=algos_table.shape[0], desc="Adding Algos...")
    for index, algo in algos_table.iterrows():
        if algo.name not in known_algo_ids:
            known_algo_ids.append(algo.name)
            algos_to_add.append((algo.name, algo['name'], algo['user'], -1))
        abar.update(1)
    abar.close()
    
    mbar = tqdm(total=matches_table.shape[0], desc="Adding Matches...")
    for index, match in matches_table.iterrows():
        if match.name not in known_match_ids:
            matches_to_add.append((match.name, match['winner_id'],match['loser_id'], match['winner_side'], None))
            all_algo_ids.add(match['winner_id'])
            all_algo_ids.add(match['loser_id'])
        mbar.update(1)
    mbar.close()

    algos_to_fetch = list(filter(lambda id: id not in known_algo_ids, all_algo_ids))
    fbar = tqdm(total=len(algos_to_fetch), desc="Fetching missing algos...")
    for algo_id in algos_to_fetch:
        fetched_algo = terminalAPI.getAlgoInfo(int(algo_id))
        username = fetched_algo[2]
        if username not in known_usernames:
            users_to_add.append(username)
        algos_to_add.append(fetched_algo) 
        fbar.update(1)
    fbar.close()


    tqdm.write("Writing to database...")
    tqdm.write(f"\n")
    tqdm.write(f"TOTAL")
    tqdm.write(f"----------------------")
    tqdm.write(f"USERS TO ADD   -- {len(users_to_add)}")
    tqdm.write(f"ALGOS TO ADD   -- {len(algos_to_add)}")
    tqdm.write(f"MATCHES TO ADD -- {len(matches_to_add)}")

    db.users.insert_many(users_to_add)
    db.algos.insert_many(algos_to_add)
    db.matches.insert_many(matches_to_add)

    tqdm.write("Done !")

