from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': 'Medium'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'Medium')
    try:
        puzzle, solution = sudoku_logic.generate_puzzle_by_difficulty(difficulty)
    except ValueError as error:
        return jsonify({'error': str(error)}), 400
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    """Return the entered cells that do not match the current solution."""
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != 0 and board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    complete = not incorrect and all(
        board[i][j] == solution[i][j]
        for i in range(sudoku_logic.SIZE)
        for j in range(sudoku_logic.SIZE)
    )
    return jsonify({'incorrect': incorrect, 'complete': complete})


@app.route('/hint', methods=['POST'])
def provide_hint():
    """Return the solution value for one currently empty cell."""
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] == 0:
                return jsonify({
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                })

    return jsonify({'error': 'There are no empty cells left'}), 400

if __name__ == '__main__':
    app.run(debug=True)