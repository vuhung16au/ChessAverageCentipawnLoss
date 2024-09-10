
import chess
import os
import sys
import chess.pgn
import chess.engine

STOCKFISH_PATH = "/usr/local/bin/stockfish"
GAME_META_DATA = "games-collection.csv"
MOVES_LOG = "logs/moves_log.txt"

ACPL_RESULT = "logs/ACPL.txt"

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
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        best_move = info["pv"][0]
        score_diff = 0

        if best_move != played_move:

            info1 = engine.analyse(board, chess.engine.Limit(depth=18), root_moves=[best_move])
            info2 = engine.analyse(board, chess.engine.Limit(depth=18), root_moves=[played_move])

            best1 = info1["score"].relative.score(mate_score=10000)
            best2 = info2["score"].relative.score(mate_score=10000)

            score_diff = abs(best1 - best2)

        with open(MOVES_LOG, "a") as f:
            f.write(f"Move: {board.san(played_move)} -> Difference: {score_diff} (Black)\n") 
            loss += score_diff
            moves += 1
        with open(MOVES_LOG, "a") as f:
            f.write(f"Move: {board.san(played_move)} -> Difference: {score_diff} (White)\n") 
            loss += score_diff
            moves += 1

        board.push(played_move)

    avg_loss = loss / moves if moves > 0 else 0

    with open(ACPL_RESULT, "a") as f:
        f.write(f"Average Centipawn Loss (ACPL) for {color.capitalize()}: {int(avg_loss)}\n")

    engine.quit()

    return avg_loss


# Example usage
# pgn_file = "PGN/set1/andrew-short.pgn"
# analyze_game(pgn_file)


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

    # stockfish_path = "/usr/local/bin/stockfish"  # Replace with the actual path to Stockfish engine

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
            f.write(f"Analyzing game: {filename}\n") 
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
        f.write(f"Average Centipawn Loss: {int(avg_centipawn_loss)}\n") 
        
    return avg_centipawn_loss
    
# def load_game_collection(filename="games-collection.csv"):
#     """
#     Loads the game collection from a CSV file.

#     Args:
#         filename (str): The path to the CSV file containing the game collection.

#     Returns:
#         A tuple containing the color and filename for each game.

#     Raises:
#         FileNotFoundError: If the CSV file is not found.

#     """

#     game_collection = []

#     with open(filename) as f:
#         lines = f.readlines()[1:]  # Skip the header

#         for line in lines:
#             color, filename = line.strip().split(", ")
#             game_collection.append((color, filename))

#     return tuple(game_collection)


if __name__ == "__main__":

    # Reset/blank the log files
    open(MOVES_LOG, "w").close()
    open(ACPL_RESULT, "w").close()

    pgn_folder = sys.argv[1] if len(sys.argv) > 1 else "./games"
    analyze_game_folder_black_white(pgn_folder)
