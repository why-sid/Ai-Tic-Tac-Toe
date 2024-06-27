from flask import Flask, render_template, jsonify, request

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    global current_player
    data = request.json
    row, col = data['row'], data['col']
    
    if board[row][col] == ' ':
        board[row][col] = current_player
        win, combo = check_win(board, current_player)
        if win:
            response = {'status': 'win', 'player': current_player, 'combo': combo}
        elif check_tie(board):
            response = {'status': 'tie'}
        else:
            current_player = 'O' if current_player == 'X' else 'X'
            response = {'status': 'continue', 'player': current_player}
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
    app.run(debug=True)
