import chess.pgn


def calculate_accuracy(pgn_file):
    total_games = 0
    total_accuracy = 0

    with open(pgn_file) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            result = game.headers["Result"]
            if result != "*":
                total_games += 1
                accuracy = calculate_game_accuracy(game)
                total_accuracy += accuracy

    if total_games > 0:
        average_accuracy = total_accuracy / total_games
        return average_accuracy
    else:
        return 0

def calculate_game_accuracy(game):
    total_moves = 0
    accurate_moves = 0

    board = game.board()
    for move in game.mainline_moves():
        total_moves += 1
        if move in board.legal_moves:
            accurate_moves += 1
        board.push(move)

    if total_moves > 0:
        accuracy = (accurate_moves / total_moves) * 100
        return accuracy
    else:
        return 0

pgn_file = "./games/transformer/10thsep-01.pgn"
average_accuracy = calculate_accuracy(pgn_file)
print(f"Average Accuracy: {average_accuracy}%")