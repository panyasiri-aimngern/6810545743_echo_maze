import csv
import os
import statistics
from pathlib import Path

DATA_FILE = Path(__file__).parent / 'data' / 'game_data.csv'

FIELDS = [
    'player', 'stage', 'round',
    'survival_time', 'steps', 'items',
    'ghost_hits', 'retries', 'score',
    'total_score', 'stage_total_hits',
    'completed', 'is_stage_clear',
]

ENC = 'utf-8-sig'


def _ensure_file():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, 'w', newline='', encoding=ENC) as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def save_record(rec: dict):
    _ensure_file()
    row = {f: rec.get(f, '') for f in FIELDS}
    with open(DATA_FILE, 'a', newline='', encoding=ENC) as f:
        csv.DictWriter(f, fieldnames=FIELDS).writerow(row)


def get_records() -> list[dict]:
    _ensure_file()
    rows = []
    with open(DATA_FILE, newline='', encoding=ENC) as f:
        for row in csv.DictReader(f):
            for field in ('stage', 'round', 'steps', 'items', 'ghost_hits', 'retries'):
                try:
                    row[field] = int(row[field]) if row[field] != '' else 0
                except ValueError:
                    row[field] = 0
            for field in ('survival_time', 'score', 'total_score', 'stage_total_hits'):
                try:
                    row[field] = float(row[field]) if row[field] != '' else 0.0
                except ValueError:
                    row[field] = 0.0
            row['completed']      = row['completed']      == 'True'
            row['is_stage_clear'] = row['is_stage_clear'] == 'True'
            rows.append(row)
    return rows


def summary_stats(values: list) -> dict | None:
    if not values:
        return None
    n      = len(values)
    mean   = statistics.mean(values)
    median = statistics.median(values)
    mn     = min(values)
    mx     = max(values)
    sd     = statistics.pstdev(values)
    return {'mean': mean, 'median': median, 'min': mn, 'max': mx, 'sd': sd, 'n': n}


def get_player_total_score(player: str) -> float:
    return sum(r['total_score'] or r['score']
               for r in get_records()
               if r['player'] == player and r['is_stage_clear'])


def get_player_total_hits(player: str) -> int:
    return int(sum(r['ghost_hits']
                   for r in get_records()
                   if r['player'] == player))


def leaderboard_score() -> list[tuple[str, float]]:
    players = {r['player'] for r in get_records()}
    data = [(p, get_player_total_score(p)) for p in players]
    return sorted(data, key=lambda x: x[1], reverse=True)[:5]


def leaderboard_hits() -> list[tuple[str, int]]:
    players = {r['player'] for r in get_records()}
    data = [(p, get_player_total_hits(p)) for p in players]
    return sorted(data, key=lambda x: x[1])[:5]
