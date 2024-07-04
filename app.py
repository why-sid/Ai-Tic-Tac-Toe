import os
from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# Initialize the Tic Tac Toe board
board = [[' ' for _ in range(3)] for _ in range(3)]
current_player = 'X'

# Check if a player has won
def check_win(board, player):
    for i in range(3):
        if all([spot == player for spot in board[i]]):
            return True, [(i, j) for j in range(3)]
        if all([board[j][i] == player for j in range(3)]):
            return True, [(j, i) for j in range(3)]
    if all([board[i][i] == player for i in range(3)]):
        return True, [(i, i) for i in range(3)]
    if all([board[i][2-i] == player for i in range(3)]):
        return True, [(i, 2-i) for i in range(3)]
    return False, []

# Check if the board is full
def check_tie(board):
    return all([spot != ' ' for row in board for spot in row])

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, maximizing_player, alpha, beta):
    # Terminal conditions: check for wins, ties, or depth limit
    result = check_game_state(board)
    if result is not None:
        return result

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None

        # Loop through all possible moves
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'  # Assume AI is 'O'
                    eval = minimax(board, depth + 1, False, alpha, beta)[0]
                    board[i][j] = ' '  # Undo move

                    if eval > max_eval:
                        max_eval = eval
                        best_move = (i, j)

                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Beta cut-off
        return max_eval, best_move

    else:
        min_eval = float('inf')
        best_move = None

        # Loop through all possible moves
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'  # Assume human player is 'X'
                    eval = minimax(board, depth + 1, True, alpha, beta)[0]
                    board[i][j] = ' '  # Undo move

                    if eval < min_eval:
                        min_eval = eval
                        best_move = (i, j)

                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cut-off
        return min_eval, best_move

def ai_move(board):
    _, best_move = minimax(board, 0, True, float('-inf'), float('inf'))
    return best_move

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    global current_player
    data = request.json
    row, col = data['row'], data['col']
    is_against_ai = data.get('isAgainstAI', False)
    
    if board[row][col] == ' ':
        board[row][col] = current_player
        win, combo = check_win(board, current_player)
        if win:
            response = {'status': 'win', 'player': current_player, 'combo': combo, 'row': row, 'col': col}
        elif check_tie(board):
            response = {'status': 'tie', 'row': row, 'col': col}
        else:
            current_player = 'O' if current_player == 'X' else 'X'
            if is_against_ai and current_player == 'O':
                ai_row, ai_col = ai_move(board)
                board[ai_row][ai_col] = current_player
                win_ai, combo_ai = check_win(board, current_player)
                if win_ai:
                    response = {'status': 'win', 'player': current_player, 'combo': combo_ai, 'row': ai_row, 'col': ai_col}
                elif check_tie(board):
                    response = {'status': 'tie', 'row': ai_row, 'col': ai_col}
                else:
                    current_player = 'X'
                    response = {'status': 'continue', 'player': current_player, 'row': ai_row, 'col': ai_col, 'board': board}
            else:
                response = {'status': 'continue', 'player': current_player, 'row': row, 'col': col, 'board': board}
    else:
        response = {'status': 'invalid'}
    
    return jsonify(response)

@app.route('/reset', methods=['POST'])
def reset():
    global board, current_player
    board = [[' ' for _ in range(3)] for _ in range(3)]
    current_player = 'X'
    return jsonify({'status': 'reset'})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
