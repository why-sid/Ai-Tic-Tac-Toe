document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const resetButton = document.getElementById('reset');
    const restartButton = document.getElementById('restart');
    const messageDiv = document.getElementById('message');
    const playHumanButton = document.getElementById('play-human');
    const playAiButton = document.getElementById('play-ai');
    let isAgainstAI = false;
    let gameActive = true; // Variable to track if the game is active

    playHumanButton.addEventListener('click', () => {
        isAgainstAI = false;
        startGame();
    });

    playAiButton.addEventListener('click', () => {
        isAgainstAI = true;
        startGame();
    });

    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            if (!gameActive) return; // Prevent move if game is not active

            const row = cell.getAttribute('data-row');
            const col = cell.getAttribute('data-col');

            fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ row: parseInt(row), col: parseInt(col), isAgainstAI: isAgainstAI })
            })
            .then(response => response.json())
            .then(data => {
                updateBoard(data);
                if (data.status === 'continue' && isAgainstAI && data.player === 'O') {
                    // Let AI make a move
                    fetch('/ai-move', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ board: data.board })
                    })
                    .then(response => response.json())
                    .then(data => updateBoard(data));
                }
            });
        });
    });

    resetButton.addEventListener('click', () => {
        fetch('/reset', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'reset') {
                resetBoard();
                messageDiv.textContent = '';
                document.querySelector('.board').style.display = 'none';
                document.querySelector('.menu').style.display = 'block';
                gameActive = true; // Reset game status
            }
        });
    });

    // Event listener for the Restart button
    restartButton.addEventListener('click', () => {
        resetBoard();
        messageDiv.textContent = '';
        restartButton.style.display = 'none'; // Hide restart button
        fetch('/reset', { method: 'POST' });
        gameActive = true; // Reset game status
    });

    function startGame() {
        document.querySelector('.menu').style.display = 'none';
        document.querySelector('.board').style.display = 'grid';
        resetButton.style.display = 'none';
        restartButton.style.display = 'none'; // Hide restart button at game start
        resetBoard();
        messageDiv.textContent = '';
        fetch('/reset', { method: 'POST' });
        gameActive = true; // Start game as active
    }

    function resetBoard() {
        cells.forEach(cell => {
            cell.textContent = '';
            cell.classList.remove('strike');
            cell.classList.remove('x');
            cell.classList.remove('o');
        });
        const backgroundDiv = document.querySelector('.winner-background');
        if (backgroundDiv) backgroundDiv.remove(); // Remove previous background
    }

    function showWinningCombo(combo) {
        combo.forEach(([row, col]) => {
            const cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
            cell.classList.add('strike');
        });
    }

    function updateBoard(data) {
        const cell = document.querySelector(`.cell[data-row="${data.row}"][data-col="${data.col}"]`);
        if (data.status === 'win') {
            cell.classList.add('tic-tac-toe-xo');
            cell.classList.add(data.player === 'X' ? 'x' : 'o');
            cell.textContent = data.player;
            showWinningCombo(data.combo);
            messageDiv.textContent = `Player ${data.player} wins!`;
            gameActive = false; // Disable further moves
            restartButton.style.display = 'block'; // Show restart button

            // Add the winning background effect
            addWinningBackground(data.player);
        } else if (data.status === 'tie') {
            cell.classList.add('tic-tac-toe-xo');
            cell.classList.add(data.player === 'X' ? 'x' : 'o');
            cell.textContent = data.player === 'O' ? 'X' : 'O';
            messageDiv.textContent = "It's a tie!";
            gameActive = false; // Disable further moves
            restartButton.style.display = 'block'; // Show restart button
        } else if (data.status === 'continue') {
            cell.classList.add('tic-tac-toe-xo');
            cell.classList.add(data.player === 'X' ? 'x' : 'o');
            cell.textContent = data.player === 'O' ? 'X' : 'O';
        } else if (data.status === 'invalid') {
            alert('This spot is already taken. Try again.');
        }
    }

    function addWinningBackground(player) {
        const backgroundDiv = document.createElement('div');
        backgroundDiv.classList.add('winner-background');

        // Create a random number of X's and O's in the background
        for (let i = 0; i < 50; i++) {
            const symbolDiv = document.createElement('div');
            symbolDiv.classList.add('symbol');
            symbolDiv.textContent = Math.random() < 0.5 ? 'X' : 'O'; // Randomly choose X or O

            // Set random positions
            symbolDiv.style.top = Math.random() * 100 + '%';
            symbolDiv.style.left = Math.random() * 100 + '%';
            symbolDiv.style.transform = `rotate(${Math.random() * 360}deg)`; // Random rotation

            backgroundDiv.appendChild(symbolDiv);
        }

        document.body.appendChild(backgroundDiv);
    }
});
