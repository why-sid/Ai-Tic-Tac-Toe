from flask import Flask, render_template, jsonify, request
import random
import math

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

# MCTS Node
class MCTSNode:
    def __init__(self, parent=None, move=None):
        self.parent = parent
        self.move = move
        self.wins = 0
        self.visits = 0
        self.children = []

    def uct(self, exploration_constant=1.41):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)

# MCTS algorithm with improved simulation
def mcts(board, player, simulations=5000):  # Increase number of simulations
    root = MCTSNode()
    for _ in range(simulations):
        node = root
        current_board = [row[:] for row in board]  # Deep copy of the board

        # Selection
        while node.children:
            node = max(node.children, key=lambda n: n.uct())
            current_board[node.move[0]][node.move[1]] = player

        # Expansion
        empty_cells = [(i, j) for i in range(3) for j in range(3) if current_board[i][j] == ' ']
        for move in empty_cells:
            child_node = MCTSNode(parent=node, move=move)
            node.children.append(child_node)

        # Simulation
        for child in node.children:
            current_board[child.move[0]][child.move[1]] = player
            if check_win(current_board, player)[0]:
                child.wins += 1
            elif check_tie(current_board):
                child.wins += 0.5  # Draw
            else:
                # Simulate optimal play instead of random
                opponent = 'O' if player == 'X' else 'X'
                while True:
                    # Check for available moves
                    empty_cells = [(i, j) for i in range(3) for j in range(3) if current_board[i][j] == ' ']
                    if not empty_cells:
                        break
                    # Choose the next move
                    move = None
                    for m in empty_cells:
                        current_board[m[0]][m[1]] = opponent
                        if check_win(current_board, opponent)[0]:  # If the opponent can win, block it
                            move = m
                            break
                        current_board[m[0]][m[1]] = ' '  # Undo move

                    if move is not None:
                        current_board[move[0]][move[1]] = opponent
                    else:
                        # If no immediate threats, play randomly
                        move = random.choice(empty_cells)
                        current_board[move[0]][move[1]] = opponent
                    
                    if check_win(current_board, opponent)[0]:
                        child.wins += 0  # Loss for child
                        break
                    elif check_tie(current_board):
                        child.wins += 0.5
                        break
                    # Switch player
                    opponent = 'X' if opponent == 'O' else 'O'

            child.visits += 1
            node.visits += 1

        # Backpropagation
        while node:
            node.visits += 1
            node = node.parent

    # Get the best move based on wins
    best_move = max(root.children, key=lambda n: n.wins).move
    return best_move


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
    best_move = mcts(board, current_player)
    row, col = best_move
    
    board[row][col] = current_player
    win, combo = check_win(board, current_player)
    if win:
        response = {'status': 'win', 'player': current_player, 'combo': combo, 'row': row, 'col': col}
    elif check_tie(board):
        response = {'status': 'tie', 'row': row, 'col': col}
    else:
        current_player = 'X' if current_player == 'O' else 'O'
        response = {'status': 'continue', 'player': current_player, 'row': row, 'col': col, 'board': board}

    return jsonify(response)

@app.route('/reset', methods=['POST'])
def reset():
    global board, current_player
    board = [[' ' for _ in range(3)] for _ in range(3)]
    current_player = 'X'
    return jsonify({'status': 'reset'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
