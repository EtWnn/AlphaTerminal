# AlphaTerminal

## Environment setup

If you're using Anaconda to manage your Python environments, you can replicate ours by running `conda env create -f environment.yml`.

## Initial setup

There are a lot of data files in this project so you will have to download/construct them first.

### 1. raw_replays downloading

Replays are the are the essential material for this project. One replay describes a match that has been played online. it is under the format '.replay' and will be stored in a dedicated folder 'raw_replays' at the root of this project. To be able to download replays there are several steps:

#### a. account creation

The first thing is to create an account on https://terminal.c1games.com. This will be needed to make requests to the Terminal API.
Once this is done, open the file `tables/terminalAPI.py` and run it. It will create a file named 'credentials'. Fill it with the credentials of the account you just created.

#### b. downloads

To download the match replays, you will need a `.env` file in the `tables` folder, containing the credentials to the database. Owner of the repo should provide these.
Then, go to the `tables` folder in a terminal, and run `python matchesDownload.py`. This will download all matches available in the database. 

> Disclaimer: the database is quite big. Downloading all replays took us nearly 24h (more than 190 Go).

#### c. database making

Now that the matches are downloaded, we can extract the data that we are interested in. This is done in the script `generalIOMaker.py`. It will be stored in the file `datasets/generalIO_v2.csv`. 

> Disclaimer: same disclaimer as above. Constructing the database took us about 16hours. More than 21 millions samples (about 30 Go) were created.


### 2. Database construction

### a. Inputs details

The input format chosen is a mixed input. The first is a 3D matrix representing the board. The first two dimensions are for the position, the third for the type of a unit. As the board is in a diamond shape, it has been shifted and transform to end as a rectangle which is easier/lighter to interpret by a model. The final shape is (15,29,7).
The second part of the input is flat: it correspond to 7 usefull metrics: `[p1_health, p1_cores, p1_bits, p2_health, p2_cores, p2_bits, turn_number]`

So our model will be a mixed CNN and FC NN. 

### b. Output details

An output corresponds to a single placement: either one firewall or one information or the possibility to stop the turn. 
For general purpose, we store the output as a string `"<unit_type>_<x>_<y>"` (except for `"stop"`)

Specific output needs will rely on this format to create the output needed (regression, classification ...)

### c. Storage

A giant CSV file located at `datasets/generalIO_v2.csv` will store the fully pre-processed match replays. It will be read batch-wise while training.

### 3. Batch generator

Given the size of the training dataset (21 million samples, so about 28Go), we made a class to handle the loading and unloading of such data into memory batch-wise. This is the BatchGenerator. It uses multithreading to pre-load batches while the model is training on the previous batch. It also handles splitting the dataset into a train, validation, and test sub-set.

### 4. Model

Training of the model is done in the notebook called `Global_Training.ipynb`.