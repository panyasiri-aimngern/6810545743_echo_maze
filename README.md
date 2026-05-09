# EcHo MaZe

## Project Description

- **Project by:** Panyasiri Aimngern
- **Game Genre:** Puzzle, Survival

EcHo MaZe is a grid-based maze game built with Python and Pygame. Navigate through the maze, collect all checkpoints, and reach the goal — but every move you make is recorded. In later rounds, your past path replays as a ghost enemy. Dodge yourself to survive.

---

## Installation

Clone this project:

```sh
git clone https://github.com/<username>/echo-maze.git
cd echo-maze
```

**Windows:**
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac:**
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Guide

**Windows:**
```bat
python main.py
```

**Mac:**
```sh
python3 main.py
```

---

## Tutorial / Usage

1. Enter your name at the start screen
2. An in-game **How to Play** guide is available — click the link on the name screen or from the main menu to learn the rules before playing
3. Select a stage (Stage 1 is unlocked by default)
4. Navigate the maze and collect all checkpoints (yellow dots)
5. Once all checkpoints are collected, the goal (green square) opens
6. Reach the goal to complete the round
7. Complete all 3 rounds to clear the stage and unlock the next one

**Controls:**

| Key | Action |
|---|---|
| W / ↑ | Move Up |
| S / ↓ | Move Down |
| A / ← | Move Left |
| D / → | Move Right |
| Space + Direction | Break wall (orange walls only, 3 hits) |
| ESC | Pause / Resume |

---

## Game Features

- **Echo System** — Your movement path from each round replays as a ghost enemy in the next round. Avoid your past self to survive
- **5 Stages** — Each stage features a larger, more complex maze with additional obstacles and tighter paths, making each stage progressively more challenging
- **Breakable Walls** — Orange walls can be broken with Space + direction (3 hits)
- **Leaderboard** — Top 5 by total score and fewest ghost hits
- **Data Analysis Report** — Statistics and visualizations of gameplay data across all players, including summary table, bar chart, line graph, boxplot, and scatter plot
- **Player Stats** — Search by name to view personal performance history
- **Sound Toggle** — Background music and sound effects with on/off toggle

---

## Known Bugs

- None

---

## Unfinished Works

- All planned features have been implemented

---

## External Sources

1. Background music and sound effects — [freesound.org](https://freesound.org) (Free to use under Creative Commons License)
2. Background image — Created with Canva
3. Font — System font loaded via pygame (see `_init_fonts()` in `game_manager.py`)
