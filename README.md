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
3. In the current setup one game will be run in detail with all the information printed such that the user can see everything that occurs, and then a sequence of games will be played, print statements for the in game details will be restricted, and the amount of games won by the mafia and by the town will be printed at the end.
   1. If one only wishes to run the in detail game, then they can comment out the line of code on line `612` of `Game.py`.
   2. If one only wishes to run the long sequence of games, they can commend out the lines of code on line `606` and `607` of `Game.py`. Additionally, one can change the parameter in the function call of the `run_games()` function on line `612` to adjust the total number of runs.
4. When one has configured the code to their desire, one can run `python Game.py` and observe the terminal outputs, and pyplot outputs in the case of the long sequence of games.
