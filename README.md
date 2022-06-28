# TownOfSalemLAMAS
# First and Second Order Knowledge Project
## Stijn De Vries, Tumi Moeng, Isabelle Tilleman
# ====================================
## 01-07-2022

Before anything, make sure that you install all the requirements as outlined in the requirements.txt file using the following command in the terminal from inside the Assignment1 folder:
`pip install -r /requirements.txt`

## Running the Model
To run the game model follow the instructions below:
1. Open a Terminal window within the `TownOfSalemLAMAS` folder
2. Edit any running variables in the `Game.py` file
   1. For example if one wishes to watch a game occur in extreme details, change `num_of_games` on line `488` to a low value, and then comment out the statements on lines `492` and `495` such that the printed output will be visible to you
   2. Alternatively, if one wishes to obersrve overall win and lose rates, change `num_of_games` on line `488` to a high number value, and then comment the statements on lines `492` and `495` such that the printed output will be invisible to you. This is beneficial because the printing will slow the code down.
3. When one has configured the code to their desire, one can run `python Game.py` and observe the terminal outputs.
