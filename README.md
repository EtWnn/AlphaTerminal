# AlphaTerminal

## Initial setup

There are a lot of data files in this project so you will have to download/construct them first.

### 1. raw_replays downloading

replays are the are the essential material for this project. One replay describes a match that has been played online. it is under the format '.replay' and will be stored in a dedicated folder 'raw_replays' at the root of this project. To be able to download replays there are several steps:

#### a. account creation

The first thing is to create an account on https://terminal.c1games.com. This will be needed to make requests to the Terminal API.
Once this is done, open the file 'tables/terminalAPI.py' and run it. It will create a file named 'credentials'. Fill it with the credentials of the account you just created.

#### b. tables setup

The only data files that are stored by this project are three tables: users_table, algos_table and matches_tables. Those are very usefull be able to download old matches. Indeed the Terminal API only allows you to access the 100 last matches of an algos. So those three tables are here to get past this limitation. The function 'updateTables' in 'table/tablesManager.py' is here to update the records.

For your local needs, you will need to execute the function 'resetMatchesBool' in 'table/tablesManager.py'.

#### c. downloads

You can now download every matches you want from the 'matches_table'. Bear in mind that each replay file weigths about 1.8Mo and there are more than 50k replay in the 'matches_table' as of now (24/12/2019).
The function 'downloadEagle' in the file 'tables/matchesDownload.py' will download every matches of the eagle algos serie. Our first work will use this serie.


### 2. Database construction

To be coming