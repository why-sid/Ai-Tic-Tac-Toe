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

# Make AI move
def ai_move(board):
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']
    if empty_cells:
        return random.choice(empty_cells)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    global current_player
    data = request.json
    row, col = data['row'], data['col']
    is_against_ai = data['isAgainstAI']
    
    if board[row][col] == ' ':
        board[row][col] = current_player
        win, combo = check_win(board, current_player)
        if win:
            response = {'status': 'win', 'player': current_player, 'combo': combo, 'row': row, 'col': col}
        elif check_tie(board):
            response = {'status': 'tie', 'row': row, 'col': col}
        else:
            current_player = 'O' if current_player == 'X' else 'X'
            response = {'status': 'continue', 'player': current_player, 'row': row, 'col': col, 'board': board}
    else:
        response = {'status': 'invalid'}
    
    return jsonify(response)

@app.route('/ai-move', methods=['POST'])
def ai_move_route():
    global current_player
    data = request.json
    row, col = ai_move(data['board'])
    
    if row is not None and col is not None:
        board[row][col] = current_player
        win, combo = check_win(board, current_player)
        if win:
            response = {'status': 'win', 'player': current_player, 'combo': combo, 'row': row, 'col': col}
        elif check_tie(board):
            response = {'status': 'tie', 'row': row, 'col': col}
        else:
            current_player = 'O' if current_player == 'X' else 'X'
            response = {'status': 'continue', 'player': current_player, 'row': row, 'col': col, 'board': board}
    else:
        response = {'status': 'tie'}
    
    return jsonify(response)

@app.route('/reset', methods=['POST'])
def reset():
    global board, current_player
    board = [[' ' for _ in range(3)] for _ in range(3)]
    current_player = 'X'
    return jsonify({'status': 'reset'})

if __name__ == "__main__":
    app.run(debug=True)
