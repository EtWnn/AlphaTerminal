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

### a. Inputs details

The format of input chosen is a mixed input. The first is a 3D matrix representing the board. The first two dimensions are for the position, the third for the type of a unit. As the board is in a diamond shape, it has been shifted and transform to end as a rectangle which is easier/lighter to interpret by a model. The final shape is (15,29,7).
The second part of the input is flat: it correspond to 7 usefull metrics: [p1_health, p1_cores, p1_bits, p2_health, p2_cores, p2_bits, turn_number]

So our model will be a mixed CNN and FC NN. 

### b. Output details

An output correspond to a single placment: either one firewall or one information or the possibility to stop the turn. 
For general purpose, we store the output as a string '"<unit_type>_<x>_<y>"' (except for '"stop"')

Specific output needs will rely on this format to create the output needed (regression, classification ...)

### c. Storage

Every image (3D matrix representing the board) will be stored in the folder "cnn_images" at the root.
A dataframe pickled as 'datasets/generalIO.pkl' will store the image_path, the image name, the flat inputs and the general output.

### d. Computation

The class 'GeneralIOMaker' and its method 'compute' are used to compute the inputs and general outputs of matches. This involve a lot of files to be created and will certainly overload your PC. So close every unnecessary thing and let your computer run (even if you get a non responding warning). About 250 files are created per match (about 850ko per match).

It will also take some times so take a book.

The function 'computeEagle' is used to create only the eagle serie inputs/outputs. 
For the first model, just run 'computeEagle([99748])' as this model will learn only from the algo number '99748'.

### e. Specific Output

to be coming