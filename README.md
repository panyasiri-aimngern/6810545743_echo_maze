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

## Project Structure

```
6810545743_echo_maze/
├── assets/                    # Game assets
│   ├── sounds/                # BGM and sound effects (.wav)
│   ├── background.png         # Background image
│   └── font.ttf               # Custom font (optional)
├── data/
│   └── game_data.csv          # Recorded gameplay statistics
├── screenshots/
│   ├── gameplay/              # Gameplay screenshots
│   │   ├── 00_tutorial_window.png
│   │   ├── 01_main_menu.png
│   │   ├── 02_name_screen.png
│   │   ├── 03_stage_select.png
│   │   ├── 04_round1(no-ghost).png
│   │   ├── 05_round2(1ghost).png
│   │   ├── 06_round3(2ghost).png
│   │   ├── 07_countdown_period.png
│   │   ├── 08_uncollected_checkpoint.png
│   │   ├── 09_locked_goal.png
│   │   ├── 10_unlocked_goal.png
│   │   ├── 11_breakable_wall.png
│   │   ├── 12_checkpoint.png
│   │   ├── 13_pause.png
│   │   ├── 14_gameover.png
│   │   ├── 15_stage_clear.png
│   │   ├── 16_leaderboard.png
│   │   ├── 17_stats.png
│   │   └── 18_player_stats.png
│   └── visualization/
│       ├── VISUALIZATION.md   # Data visualization documentation
│       ├── 01_overview.png
│       ├── 02_summary_statistics_table.png
│       ├── 03_bar_survival_time.png
│       ├── 04_line_steps.png
│       ├── 05_boxplot_ghost.png
│       ├── 06_scatter_stepsVSscore.png
│       └── 07_clear_rate.png
├── constants.py               # Grid settings, colors, and map layouts
├── main.py                    # Entry point
├── game_manager.py            # Main game controller
├── player.py                  # Player movement and path recording
├── ghost.py                   # Ghost replay logic
├── map.py                     # Maze grid and rendering
├── mission.py                 # Checkpoint tracking
├── ui.py                      # Panel, Button, TextInput components
├── stats.py                   # CSV data recording and statistics
├── data_window.py             # Data Analysis window (Tkinter + Matplotlib)
├── visualization.py           # Static visualization export
├── tutorial.py                # How to Play window (Tkinter)
├── requirements.txt           # Python dependencies
├── README.md                  # Installation and usage guide
├── DESCRIPTION.md             # Project description and documentation
├── echo_maze_uml.pdf          # UML class diagram
├── proposal.pdf               # Original project proposal
├── LICENSE                    # MIT License
└── .gitignore
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

### Getting Started
1. Enter your name at the start screen — progress is saved per name
2. An in-game **How to Play** guide is available — click `→ How to Play` on the name screen to learn the rules before playing
3. Select a stage from the Stage Select screen (Stage 1 is unlocked by default)

### How to Play
Each stage has **3 rounds**:

| Round | Ghosts | Description |
|---|---|---|
| Round 1 | None | Explore the maze freely — your movement is recorded |
| Round 2 | 1 ghost | Your Round 1 path replays as a ghost enemy |
| Round 3 | 2 ghosts | Both Round 1 and Round 2 paths replay simultaneously |

**Objective each round:**
1. Navigate the maze and collect all **checkpoints** (yellow dots)
2. Once all checkpoints are collected, the **goal** (green square) unlocks
3. Reach the goal to complete the round

**If you get caught by a ghost:**
- The round ends immediately
- You can choose to **Restart Round** — ghost recordings are kept, round replays from the beginning
- Or **Retry Stage** — erases all ghost recordings and restarts from Round 1

**Grace Period:**
- At the start of rounds with ghosts, a **3-second countdown** appears
- Ghosts are frozen during this time — use it to reposition before they start moving

**Breakable Walls:**
- Orange walls can be broken to open new shortcuts
- Stand next to an orange wall and press **Space + the direction toward it**
- Requires **3 hits** to fully break

**Clearing a Stage:**
- Complete all 3 rounds to clear the stage and unlock the next one
- Score is calculated as `10,000 − (time × 10)` — faster completion = higher score

**Statistics:**
- Access from Main Menu → **Stats**
- **Data Analysis Report** — overall charts and statistics across all players
- **Player Stats** — search by name to view your personal performance history

**Leaderboard:**
- Access from Main Menu → **Leaderboard**
- Top 5 by total score and top 5 by fewest ghost hits

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
