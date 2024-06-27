document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const resetButton = document.getElementById('reset');
    const messageDiv = document.getElementById('message');

    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            const row = cell.getAttribute('data-row');
            const col = cell.getAttribute('data-col');

            fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ row: parseInt(row), col: parseInt(col) })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'win') {
                    cell.classList.add('tic-tac-toe-xo');
                    cell.classList.add(data.player === 'X' ? 'x' : 'o');
                    cell.textContent = data.player;
                    showWinningCombo(data.combo);
                    messageDiv.textContent = `Player ${data.player} wins!`;
                } else if (data.status === 'tie') {
                    cell.classList.add('tic-tac-toe-xo');
                    cell.classList.add(data.player === 'X' ? 'x' : 'o');
                    cell.textContent = data.player === 'O' ? 'X' : 'O';
                    messageDiv.textContent = "It's a tie!";
                } else if (data.status === 'continue') {
                    cell.classList.add('tic-tac-toe-xo');
                    cell.classList.add(data.player === 'X' ? 'x' : 'o');
                    cell.textContent = data.player === 'O' ? 'X' : 'O';
                } else if (data.status === 'invalid') {
                    alert('This spot is already taken. Try again.');
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
            }
        });
    });

    function resetBoard() {
        cells.forEach(cell => {
            cell.textContent = '';
            cell.classList.remove('strike');
            cell.classList.remove('x');
            cell.classList.remove('o');
        });
    }

    function showWinningCombo(combo) {
        combo.forEach(([row, col]) => {
            const cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
            cell.classList.add('strike');
        });
    }
});
