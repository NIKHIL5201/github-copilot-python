import copy
import random

SIZE = 9
EMPTY = 0

DIFFICULTY_LEVELS = {
    "Easy": 45,
    "Medium": 36,
    "Hard": 28,
}


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def is_valid_puzzle(board):
    """Return True when the board contains no duplicate values in any row, column, or 3x3 box."""
    for row in range(SIZE):
        seen = set()
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if value in seen:
                return False
            seen.add(value)

    for col in range(SIZE):
        seen = set()
        for row in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if value in seen:
                return False
            seen.add(value)

    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            seen = set()
            for row in range(start_row, start_row + 3):
                for col in range(start_col, start_col + 3):
                    value = board[row][col]
                    if value == EMPTY:
                        continue
                    if value in seen:
                        return False
                    seen.add(value)
    return True


def count_solutions(board, limit=2):
    """Return how many solutions exist, stopping as soon as the limit is reached."""
    row_mask = [0] * SIZE
    col_mask = [0] * SIZE
    box_mask = [0] * SIZE

    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if value < 1 or value > SIZE:
                return 0
            bit = 1 << (value - 1)
            box_index = (row // 3) * 3 + (col // 3)
            if row_mask[row] & bit or col_mask[col] & bit or box_mask[box_index] & bit:
                return 0
            row_mask[row] |= bit
            col_mask[col] |= bit
            box_mask[box_index] |= bit

    full_mask = (1 << SIZE) - 1
    empty_cells = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
        if board[row][col] == EMPTY
    ]

    def search():
        best_row = -1
        best_col = -1
        best_options = 0
        best_count = SIZE + 1

        for row, col in empty_cells:
            if board[row][col] != EMPTY:
                continue
            box_index = (row // 3) * 3 + (col // 3)
            options = full_mask & ~(row_mask[row] | col_mask[col] | box_mask[box_index])
            count = options.bit_count()
            if count == 0:
                return 0
            if count < best_count:
                best_row = row
                best_col = col
                best_options = options
                best_count = count
                if count == 1:
                    break

        if best_row == -1:
            return 1

        total = 0
        options = best_options
        while options:
            bit = options & -options
            value = bit.bit_length()
            box_index = (best_row // 3) * 3 + (best_col // 3)
            board[best_row][best_col] = value
            row_mask[best_row] |= bit
            col_mask[best_col] |= bit
            box_mask[box_index] |= bit
            total += search()
            board[best_row][best_col] = EMPTY
            row_mask[best_row] ^= bit
            col_mask[best_col] ^= bit
            box_mask[box_index] ^= bit
            if total >= limit:
                return total
            options ^= bit
        return total

    return search()


def has_unique_solution(board):
    """Return True only when the puzzle has exactly one valid solution."""
    return count_solutions(board, limit=2) == 1


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board, clues):
    """Remove cells while preserving uniqueness, stopping once the target clue count is reached."""
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)
    clue_count = sum(value != EMPTY for row in board for value in row)

    while clue_count > clues:
        for row, col in positions:
            if board[row][col] == EMPTY:
                continue
            value = board[row][col]
            board[row][col] = EMPTY
            if not has_unique_solution(board):
                board[row][col] = value
            else:
                clue_count -= 1
            if clue_count <= clues:
                return


def generate_puzzle(clues=35):
    """Generate a puzzle and its solution, ensuring the puzzle has exactly one valid solution."""
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    puzzle = deep_copy(solution)
    remove_cells(puzzle, clues)
    return puzzle, solution


def generate_puzzle_by_difficulty(level="Medium", clues=None):
    """Generate a puzzle for a given difficulty level and return it with its solution."""
    if level not in DIFFICULTY_LEVELS:
        raise ValueError("Difficulty must be one of: Easy, Medium, Hard")

    target_clues = clues if clues is not None else DIFFICULTY_LEVELS[level]

    if target_clues < 17 or target_clues > 81:
        raise ValueError("Number of clues must be between 17 and 81")

    puzzle = create_empty_board()
    fill_board(puzzle)
    solution = deep_copy(puzzle)
    remove_cells(puzzle, target_clues)
    return puzzle, solution
