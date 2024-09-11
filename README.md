# What This Tool Does 

This tool calculates the Average of Average Centipawn Loss (ACPL) in multiple chess games.

# Why I Created This Tool?

I created this tool to assess players' overall performance, consistency, and strength in a chess tournament.

# Main Features 

- Calculate ACPL for PGN game(s) 
- Find missed wins, blunders, mistakes, inaccuracies

# How To Use This Tool

1. Set up a virtual environment: `virtualenv venv`
2. Activate the virtual environment: `source ./venv/bin/activate`
3. Install the required dependencies: `pip install -r requirements.txt`
3. Put your games under "games" folder and update `games-collection.csv` accordingly. 
4. Run the tool: `./tool.py /path/to/folder/contains/all/PGNfiles/`

# What Is the Meaning of Average ACPLs?

The Average ACPL indicates the consistency of a player's performance in the games they play. For example, if a player plays 9 games in a tournament, their moves may vary in quality. Some moves may have a low Centipawn Loss (CPL) for good moves, while others may have a high CPL for bad moves (blunders, mistakes, inaccuracies). The average CPL for all the moves played in the tournament serves as a good indicator of the player's performance.

# Sample Run 

```
Analyzing game: carlsen_firouzja_2021.pgn
Average Centipawn Loss (ACPL) for White: 130 -> ACPL for the first game
Analyzing game: dominguez_perez_carlsen_2009.pgn
Average Centipawn Loss (ACPL) for Black: 27 -> ACPL for the 2nd game
Analyzing game: kramnik_carlsen_2008.pgn
Average Centipawn Loss (ACPL) for Black: 14 -> ACPL for the first game
Average Centipawn Loss: 28 -> Average ACPL for all game listed 
``` 

Keep reading if you want to learn more about PGN, centipawn, ACPL

# What Is a PGN File

A PGN (Portable Game Notation) file is a plain text file format commonly used to store and share chess game data. It includes information such as the moves played, game metadata, and optional annotations or comments.

# What Is a Centipawn?

A centipawn is a unit of measurement used in chess to evaluate the strategic aspects of a position and determine which player has an advantage. It is not a formal part of the game itself.

# What is an Average Centipawn Loss (ACPL)?

Average Centipawn Loss (ACPL) measures the "value" a player loses by making incorrect moves during a chess game. It indicates the accuracy of a player's moves. Super grandmasters typically have an average loss between 10 and 20. Elite players use ACPL to assess the quality of their games. For example, GM Magnus Carlsen achieved a single-digit average ACPL in the 2018 World Chess Championship. Understanding ACPL is important for evaluating chess games.

# What Is The Benefit Of Using Centipawns?

Centipawns provide a standardized unit of measurement for evaluating positional advantages in chess. For instance, a one-pawn advantage is equivalent to 1 centipawn, while a one-rook advantage is equivalent to 5 centipawns (equivalent to five pawns). This allows for a more precise assessment of positional advantages in the game.

# Why My ACPL Are Not the Same with Other Chess Apps?

Because there every chess apps calculate ACPL with different settings. 
