
import math
import chess
import os
import sys
import chess.pgn
import chess.engine

STOCKFISH_PATH = "/usr/local/bin/stockfish"
STOCKFISH_DEPTH = 15

GAME_META_DATA = "games-collection.csv"
MOVES_LOG = "logs/99_moves_log.txt"

log_files = {
    "MISSED_WIN_LOG": "logs/00_missed_wins_log.txt",
    "BLUNDER_LOG": "logs/01_blunders_log.txt",
    "MISTAKE_LOG": "logs/02_mistakes_log.txt",
    "INACCURACY_LOG": "logs/03_inaccuracies_log.txt"
}

thresholds = {
    "MISSED_WIN_THRESHOLD": 2000,
    "BLUNDER_THRESHOLD": 150,
    "MISTAKE_THRESHOLD": 80,
    "INACCURACY_LOG_THRESHOLD": 30
}

MISSED_WIN_LOG = log_files["MISSED_WIN_LOG"]
MISSED_WIN_THRESHOLD = thresholds["MISSED_WIN_THRESHOLD"]

BLUNDER_LOG = log_files["BLUNDER_LOG"]
BLUNDER_THRESHOLD = thresholds["BLUNDER_THRESHOLD"]

MISTAKE_LOG = log_files["MISTAKE_LOG"]
MISTAKE_THRESHOLD = thresholds["MISTAKE_THRESHOLD"]

INACCURACY_LOG = log_files["INACCURACY_LOG"]
INACCURACY_LOG_THRESHOLD = thresholds["INACCURACY_LOG_THRESHOLD"]

ACPL_RESULT = "logs/09_acpl.txt"
ACCURACY_RESULT = "logs/10_accuracy.txt"

def write_move_to_log(board, played_move, score_diff):
    """
    Writes the move to the appropriate log file based on the score difference.

    Args:
        board (chess.Board): The current board position.
        played_move (chess.Move): The move played by the player.
        score_diff (int): The score difference between the played move and the best move.

    Returns:
        None

    """

    if score_diff >= MISSED_WIN_THRESHOLD:
        log_file = MISSED_WIN_LOG
    elif score_diff >= BLUNDER_THRESHOLD:
        log_file = BLUNDER_LOG
    elif score_diff >= MISTAKE_THRESHOLD:
        log_file = MISTAKE_LOG
    elif score_diff >= INACCURACY_LOG_THRESHOLD:
        log_file = INACCURACY_LOG
    else:
        return

    with open(log_file, "a") as f:
        f.write(f"Move: {board.fullmove_number}.{board.san(played_move)} -> Difference: {score_diff}\n")

# TODO 
# Ref. https://lichess.org/page/accuracy
# Calculate the accuracy of the player for "color" in the game "pgn_file"
# Accuracy% represents how much you deviated from the best moves, i.e. how much your winning chances decreased with each move you made. Indeed in chess, from a chess engine standpoint, good moves don't exist! You can't increase your winning chances by playing a move, only reduce them if you make a mistake. Because if you have a good move to play, then it means the position was already good for you before you played it.
# First, calculate Win% = 50 + 50 * (2 / (1 + exp(-0.00368208 * centipawns)) - 1)
# Then, compute Accuracy%
# Now that we have a Win% number for each position, we can compute the accuracy of a move by comparing the Win% before and after the move. Here's the equation:
# Accuracy% = 103.1668 * exp(-0.04354 * (winPercentBefore - winPercentAfter)) - 3.1669
def calculate_accuracy(pgn_file, color):
    """
    Calculates the accuracy of the player for the specified color in the given game.

    Args:
        pgn_file (str): The path to the PGN file containing the chess game.
        color (str): The color to calculate the accuracy for ("black" or "white").

    Returns:
        The accuracy percentage of the player.

    Raises:
        FileNotFoundError: If the PGN file is not found.

    """

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    with open(pgn_file) as f:
        game = chess.pgn.read_game(f)

    board = game.board()
    accuracy = 0
    total_moves = 0

    for played_move in game.mainline_moves():
        # info_before = engine.analyse(board, chess.engine.Limit(time=1000))
        info_before = engine.analyse(board, chess.engine.Limit(depth=STOCKFISH_DEPTH))

        # Win% = 50 + 50 * (2 / (1 + exp(-0.00368208 * centipawns)) - 1)

        win_percent_before = 50 + 50 * (2 / (1 + math.exp(-0.00368208 * info_before["score"].relative.score(mate_score=10000))) - 1)

        board.push(played_move)

        # info_after = engine.analyse(board, chess.engine.Limit(time=1000))
        info_after = engine.analyse(board, chess.engine.Limit(depth=STOCKFISH_DEPTH))

        win_percent_after = 50 + 50 * (2 / (1 + math.exp(-0.00368208 * info_after["score"].relative.score(mate_score=10000))) - 1)

        # Calculate the accuracy of the move. Ref. https://lichess.org/page/accuracy
        accuracy += 103.1668 * math.exp(-0.04354 * (win_percent_before - win_percent_after)) - 3.1669
        total_moves += 1

    engine.quit()

    avg_accuracy = accuracy / total_moves if total_moves > 0 else 0

    # Write the accuracy to the log file ACCURACY_RESULT
    with open(ACCURACY_RESULT, "a") as f:
        f.write(f"Accuracy: {color.capitalize()}: {avg_accuracy}\n")


    return avg_accuracy

def analyze_game(pgn_file, color):
    """
    Analyzes a chess game stored in a PGN file using Stockfish engine.

    Args:
        pgn_file (str): The path to the PGN file containing the chess game.
        color (str): The color to calculate the average centipawn loss for ("black" or "white").

    Returns:
        The average centipawn loss for the specified color.

    Raises:
        FileNotFoundError: If the PGN file or Stockfish engine executable is not found.

    """

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    with open(pgn_file) as f:
        game = chess.pgn.read_game(f)

    board = game.board()
    loss = 0
    moves = 0

    for played_move in game.mainline_moves():

        depth = 15
        info = engine.analyse(board, chess.engine.Limit(depth=STOCKFISH_DEPTH))
        best_move = info["pv"][0]
        score_diff = 0

        if best_move != played_move:
            info1 = engine.analyse(board, chess.engine.Limit(depth=STOCKFISH_DEPTH), root_moves=[best_move])
            info2 = engine.analyse(board, chess.engine.Limit(depth=STOCKFISH_DEPTH), root_moves=[played_move])

            best1 = info1["score"].relative.score(mate_score=10000)
            best2 = info2["score"].relative.score(mate_score=10000)

            score_diff = abs(best1 - best2)

            # TODO consider how to calculate centipawnloss if a move is a MISSED_WIN?
            score_diff = 0 if score_diff >= MISSED_WIN_THRESHOLD else score_diff

            write_move_to_log(board, played_move, score_diff)
       
        with open(MOVES_LOG, "a") as f:
            # print the number of moves and the move itself
            # f.write(f"Move pair: {board.fullmove_number}\n")
            
            # print the move and the score difference   
            f.write(f"Move: {board.fullmove_number}.{board.san(played_move)} -> Difference: {score_diff} (Black)\n") 
            loss += score_diff
            moves += 1
        with open(MOVES_LOG, "a") as f:
            f.write(f"Move: {board.fullmove_number}.{board.san(played_move)} -> Difference: {score_diff} (White)\n") 
            loss += score_diff
            moves += 1

        board.push(played_move)

    avg_loss = loss / moves if moves > 0 else 0

    with open(ACPL_RESULT, "a") as f:
        f.write(f"ACPL: {color.capitalize()}: {int(avg_loss)}\n")

    engine.quit()

    return avg_loss


def analyze_game_folder_black_white(pgn_folder):
    """
    Analyzes a folder containing PGN games using Stockfish engine and calculates the average centipawn loss for Black and White.

    Args:
        pgn_folder (str): The path to the folder containing the PGN games.

    Returns:
        None

    Raises:
        FileNotFoundError: If the PGN folder or Stockfish engine executable is not found.

    """

    total_black_loss = 0
    total_white_loss = 0
    total_games = 0

    # Skip the header
    with open(os.path.join(pgn_folder, GAME_META_DATA)) as f:
        lines = f.readlines()[1:]
    
    for line in lines:
        color, filename = line.strip().split(",")
        pgn_file = os.path.join(pgn_folder, filename)
        with open(ACPL_RESULT, "a") as f:
            f.write(f"Analyzing game: {filename}: {color}: ") 
        if color.lower() == "black":
            black_loss = analyze_game(pgn_file, "black")
            white_loss = 0
        elif color.lower() == "white":
            black_loss = 0
            white_loss = analyze_game(pgn_file, "white")
        else:
            black_loss = 0
            white_loss = 0

        if color.lower() == "black":
            total_black_loss += black_loss
        elif color.lower() == "white":
            total_white_loss += white_loss

        total_games += 1

    avg_black_loss = total_black_loss / total_games if total_games > 0 else 0
    avg_white_loss = total_white_loss / total_games if total_games > 0 else 0

    avg_centipawn_loss = (avg_black_loss + avg_white_loss) / 2

    with open(ACPL_RESULT, "a") as f:
        f.write(f"Overall Average Centipawn Loss: {int(avg_centipawn_loss)}\n") 
        
    return avg_centipawn_loss
    
# Reset the log files
def reset_logs():
    open(ACPL_RESULT, "w").close()
    open(ACCURACY_RESULT, "w").close()

    open(MISSED_WIN_LOG, "w").close()
    open(MOVES_LOG, "w").close()
    open(BLUNDER_LOG, "w").close()
    open(INACCURACY_LOG, "w").close()
    open(MISTAKE_LOG, "w").close()

    return None

def test_calculate_accuracy():
    pgn_file = "games/transformer/10thsep-01.pgn"
    color = "white"
    print(calculate_accuracy(pgn_file, color))
    print("")
    pgn_file = "games/transformer/10thsep-02.pgn"
    color = "black"
    print(calculate_accuracy(pgn_file, color))
    print("")


def test_analyze_game_folder_black_white():
    pgn_folder = "games"
    analyze_game_folder_black_white(pgn_folder)

def test_analyze_game():
    pgn_file = "games/transformer/10thsep-01.pgn"
    color = "white"
    print(analyze_game(pgn_file, color))
    print("")
    pgn_file = "games/transformer/10thsep-02.pgn"
    color = "black"
    print(analyze_game(pgn_file, color))
    print("")

"""
TODO fix 
transformer outputs: 
741.2830261396034
541.2378874130336
"""

if __name__ == "__main__":

    # Reset/blank the log files
    reset_logs()

    # TODO validate the results
    # test_calculate_accuracy()

    # the first argument is the folder containing the games
    pgn_folder = sys.argv[1] if len(sys.argv) > 1 else "./games"
    analyze_game_folder_black_white(pgn_folder)
