import pytest

from sudoku_logic import (
    EMPTY,
    SIZE,
    count_solutions,
    create_empty_board,
    fill_board,
    generate_puzzle,
    generate_puzzle_by_difficulty,
    has_unique_solution,
    is_safe,
)


def _is_valid_solution(board):
    for row in board:
        if sorted(row) != list(range(1, SIZE + 1)):
            return False

    for col in range(SIZE):
        column = [board[row][col] for row in range(SIZE)]
        if sorted(column) != list(range(1, SIZE + 1)):
            return False

    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            values = []
            for row in range(start_row, start_row + 3):
                for col in range(start_col, start_col + 3):
                    values.append(board[row][col])
            if sorted(values) != list(range(1, SIZE + 1)):
                return False

    return True


def test_create_empty_board_returns_9_by_9_zero_grid():
    board = create_empty_board()

    assert len(board) == SIZE
    assert all(len(row) == SIZE for row in board)
    assert all(value == EMPTY for row in board for value in row)


def test_is_safe_rejects_conflicts_in_row_column_and_box():
    board = create_empty_board()

    assert is_safe(board, 0, 0, 5) is True

    board[0][1] = 5
    assert is_safe(board, 0, 0, 5) is False

    board = create_empty_board()
    board[1][0] = 5
    assert is_safe(board, 0, 0, 5) is False

    board = create_empty_board()
    board[1][1] = 5
    assert is_safe(board, 0, 0, 5) is False

    assert is_safe(board, 0, 0, 4) is True


def test_fill_board_produces_a_valid_complete_solution():
    board = create_empty_board()

    assert fill_board(board) is True
    assert _is_valid_solution(board)
    assert all(value != EMPTY for row in board for value in row)


def test_generate_puzzle_returns_valid_puzzle_and_solution():
    puzzle, solution = generate_puzzle(clues=25)

    assert len(puzzle) == SIZE
    assert len(solution) == SIZE
    assert all(len(row) == SIZE for row in puzzle)
    assert all(len(row) == SIZE for row in solution)
    assert _is_valid_solution(solution)

    empty_count = sum(value == EMPTY for row in puzzle for value in row)
    assert empty_count == 56
    assert empty_count > 0

    for row in range(SIZE):
        for col in range(SIZE):
            if puzzle[row][col] != EMPTY:
                assert puzzle[row][col] == solution[row][col]


def test_has_unique_solution_checks_validity_and_uniqueness():
    solved_board = create_empty_board()
    assert fill_board(solved_board) is True
    assert has_unique_solution(solved_board) is True

    invalid_board = [row[:] for row in solved_board]
    invalid_board[0][0] = 1
    invalid_board[0][1] = 1
    assert has_unique_solution(invalid_board) is False

    multiple_solution_board = create_empty_board()
    assert count_solutions(multiple_solution_board) > 1
    assert has_unique_solution(multiple_solution_board) is False


def test_generate_puzzle_by_difficulty_creates_a_unique_solution():
    for level in ("Easy", "Medium", "Hard"):
        puzzle, solution = generate_puzzle_by_difficulty(level)

        assert len(puzzle) == SIZE
        assert len(solution) == SIZE
        assert _is_valid_solution(solution)
        assert has_unique_solution(puzzle) is True
        assert sum(value != EMPTY for row in puzzle for value in row) >= 17
