Project Instructions for GitHub Copilot
Project Overview
This is a Flask-based Sudoku game being refactored from legacy code into a modern,
modular application with difficulty levels, a timer, hints, live validation, and a
top-10 local leaderboard.
Code Style & Standards
Use Python 3.10+ syntax and features (type hints, f-strings, dataclasses where useful).
Follow PEP8 formatting.
Every function must have a short docstring explaining what it does, its parameters,
and its return value.
Prefer small, single-responsibility functions over long ones.
Use clear, descriptive variable and function names (no single-letter names except
loop counters like `i`, `j` in tight loops).
Project Structure
Keep Flask routes in `app.py` — routes should be thin and delegate logic to helper
modules.
Keep all Sudoku generation/validation/solving logic in `sudoku_logic.py`.
Frontend JavaScript should be organized by feature (timer, board rendering,
scoreboard, dark mode) rather than one giant script file.
CSS should use CSS variables for colors so light/dark mode can be toggled easily.
Error Handling
Never let an exception crash the Flask server; use try/except around user input
handling and return a clear JSON error message with an appropriate HTTP status code.
Validate all incoming request data (e.g., cell values, difficulty) before using it.
Testing
Use `pytest` for all backend tests.
Every new function in `sudoku_logic.py` should have at least one corresponding test.
Run the full test suite after every feature change before moving to the next task.
Working with Copilot Suggestions
Do not blindly accept all suggestions — review each one for correctness and fit
with this project's style before accepting.
If a suggestion is overly complex or doesn't fit the existing structure, ask for
a simpler alternative or reject and write it manually.
Prefer suggestions that reuse existing helper functions over duplicating logic.
Feature Requirements (for context)
Difficulty selector (Easy/Medium/Hard) controls number of prefilled cells.
Every generated puzzle must have exactly one unique solution.
Hint button fills and locks one correct empty cell.
Check button highlights incorrect entries without revealing answers.
Timer tracks elapsed time per game.
Completed games save name, time, difficulty, and hint count to a top-10 list in
browser localStorage, persisting across sessions.
Dark mode toggle updates the entire UI consistently.~