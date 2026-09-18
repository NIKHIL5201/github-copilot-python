// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuTop10';
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let gameCompleted = false;
let currentDifficulty = 'Medium';
let hintsUsed = 0;
let latestCheckRequest = 0;

// Create the empty 9-by-9 input grid and attach cell listeners.
function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.box = Math.floor(i / 3) * 3 + Math.floor(j / 3);
      input.addEventListener('input', handleCellInput);
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

// Apply the saved theme and keep the theme control in sync with it.
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem('sudokuTheme', theme);
  const themeToggle = document.getElementById('theme-toggle');
  const darkModeActive = theme === 'dark';
  themeToggle.innerText = darkModeActive ? 'Light Mode' : 'Dark Mode';
  themeToggle.setAttribute(
    'aria-label',
    darkModeActive ? 'Switch to light mode' : 'Switch to dark mode'
  );
}

// Switch between the light and dark color themes.
function toggleTheme() {
  const currentTheme = document.documentElement.dataset.theme || 'light';
  applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
}

// Fill the grid with a new puzzle and lock its prefilled cells.
function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

// Read the current values from the grid as a numeric board.
function readBoard() {
  const inputs = document.querySelectorAll('.sudoku-cell');
  const board = Array.from({length: SIZE}, () => Array(SIZE).fill(0));
  inputs.forEach((input) => {
    const row = Number(input.dataset.row);
    const col = Number(input.dataset.col);
    board[row][col] = input.value ? Number(input.value) : 0;
  });
  return board;
}

// Display a status message without changing the board state.
function showMessage(text, color = '#d32f2f') {
  const message = document.getElementById('message');
  message.innerText = text;
  message.style.color = color;
}

// Return whether a value conflicts with another value in its row, column, or box.
function hasConflict(board, row, col, value) {
  if (!value) return false;
  for (let index = 0; index < SIZE; index++) {
    if (index !== col && board[row][index] === value) return true;
    if (index !== row && board[index][col] === value) return true;
  }
  const startRow = row - row % 3;
  const startCol = col - col % 3;
  for (let boxRow = startRow; boxRow < startRow + 3; boxRow++) {
    for (let boxCol = startCol; boxCol < startCol + 3; boxCol++) {
      if ((boxRow !== row || boxCol !== col) && board[boxRow][boxCol] === value) {
        return true;
      }
    }
  }
  return false;
}

// Sanitize a typed value and immediately highlight local Sudoku conflicts.
function handleCellInput(event) {
  const input = event.target;
  input.value = input.value.replace(/[^1-9]/g, '').slice(0, 1);
  input.classList.remove('incorrect', 'conflict');
  const board = readBoard();
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  if (hasConflict(board, row, col, board[row][col])) {
    input.classList.add('conflict');
    showMessage('This number conflicts with its row, column, or box.');
  } else if (!gameCompleted) {
    showMessage('');
    if (board.every((rowValues) => rowValues.every((value) => value !== 0))) {
      checkSolution();
    }
  }
}

// Start or restart the elapsed-time counter for the current game.
function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

// Stop the elapsed-time counter when the game ends or a new game starts.
function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

// Render elapsed seconds in a compact minutes-and-seconds format.
function updateTimerDisplay() {
  document.getElementById('timer').innerText = formatTime(elapsedSeconds);
}

// Format a number of seconds for the timer and leaderboard.
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainingSeconds = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainingSeconds}`;
}

// Read, sort, and trim the browser-persisted leaderboard entries.
function getLeaderboard() {
  try {
    const savedScores = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');
    return Array.isArray(savedScores)
      ? savedScores.sort((first, second) => first.timeSeconds - second.timeSeconds).slice(0, 10)
      : [];
  } catch (error) {
    return [];
  }
}

// Save a completed score in localStorage, keeping only the ten fastest times.
function saveScoreToLeaderboard(name, timeSeconds, difficulty, hintCount) {
  const scores = getLeaderboard();
  scores.push({name, timeSeconds, difficulty, hintCount});
  scores.sort((first, second) => first.timeSeconds - second.timeSeconds);
  localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores.slice(0, 10)));
  renderLeaderboard();
}

// Render the localStorage leaderboard using text nodes so player names stay safe.
function renderLeaderboard() {
  const leaderboardBody = document.getElementById('leaderboard-body');
  leaderboardBody.innerHTML = '';
  getLeaderboard().forEach((score, index) => {
    const row = document.createElement('tr');
    [index + 1, score.name, formatTime(score.timeSeconds), score.difficulty].forEach((value) => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.appendChild(cell);
    });
    leaderboardBody.appendChild(row);
  });
}

// Lock one correct solution value into the first empty cell returned by the server.
async function handleHint() {
  if (gameCompleted) return;
  const response = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: readBoard()})
  });
  const data = await response.json();
  if (data.error) {
    showMessage(data.error);
    return;
  }
  const input = document.querySelector(
    `.sudoku-cell[data-row="${data.row}"][data-col="${data.col}"]`
  );
  input.value = data.value;
  input.disabled = true;
  input.classList.add('hinted');
  hintsUsed += 1;
  showMessage('A correct cell has been filled and locked.', '#388e3c');
  if (readBoard().every((rowValues) => rowValues.every((value) => value !== 0))) {
    checkSolution();
  }
}

// Fetch a fresh puzzle, reset the game state, and start its timer.
async function newGame() {
  const selectedDifficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${selectedDifficulty}`);
  const data = await res.json();
  if (data.error) {
    showMessage(data.error);
    return;
  }
  renderPuzzle(data.puzzle);
  gameCompleted = false;
  currentDifficulty = data.difficulty;
  hintsUsed = 0;
  document.getElementById('hint').disabled = false;
  showMessage('');
  startTimer();
}

// Check the current board and stop the timer after a correct completion.
async function checkSolution() {
  const requestId = ++latestCheckRequest;
  const inputs = document.querySelectorAll('.sudoku-cell');
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: readBoard()})
  });
  const data = await res.json();
  if (requestId !== latestCheckRequest) return;
  if (data.error) {
    showMessage(data.error);
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    inp.classList.remove('incorrect');
    if (!inp.disabled && incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }
  if (data.complete) {
    gameCompleted = true;
    stopTimer();
    document.getElementById('hint').disabled = true;
    const completionTime = formatTime(elapsedSeconds);
    showMessage(`Congratulations! You solved it in ${completionTime}.`, '#388e3c');
    const playerName = window.prompt('Congratulations! Enter your name for the Top 10 leaderboard:');
    if (playerName && playerName.trim()) {
      saveScoreToLeaderboard(
        playerName.trim(),
        elapsedSeconds,
        currentDifficulty,
        hintsUsed
      );
    }
  } else {
    showMessage(incorrect.size ? 'Some cells are incorrect.' : 'Keep going!');
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', handleHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  applyTheme(document.documentElement.dataset.theme || 'light');
  renderLeaderboard();
  // initialize
  newGame();
});