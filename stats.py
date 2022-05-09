import csv
from pathlib import Path

from rich.table import Table

from game import Game
from utils import get_timestamped_file_path

GAME_STATS_DIR = Path(__file__).parent / "game-stats"
GAME_STATS_DIR.mkdir(exist_ok=True)
GAME_STATS_FILE_PATH = get_timestamped_file_path(dir=GAME_STATS_DIR, suffix=".csv")

for p in GAME_STATS_DIR.iterdir():
    if p.name.startswith("game-history"):
        p.unlink()


class GameStats:
    """Utility singleton to help track & display historical stats across games."""

    full_history: list[Game] = []
    _games: list[Game] = []
    AUTO_SAVE = countdown = 100

    @classmethod
    def update_game(cls, game: Game) -> None:
        """Update the statistics for the most recently tracked game."""
        cls._games[-1] = game
        cls.full_history.append(game)

    @classmethod
    def new_game(cls, game: Game) -> None:
        """Start tracking statistics for a new game."""
        if cls.full_history:
            cls.save_latest()
        cls._games.append(game)
        cls.full_history = [game]

    headers = ("game #", "tick #", "score")

    @classmethod
    def rows(cls, colors: bool = True, count: int = 10) -> list[list[str]]:
        """Return rows of game stats.

        Use colors=False for machine-parseable format, True for terminal display.
        Use count=0 to return all rows of historical data.
        """
        # reversed to put most recent at top of table
        _rows = [
            [
                str(game_number),
                str(game.ticks),
                str(game.score),
            ]
            for game_number, game in reversed(
                list(enumerate(cls._games[-count:], start=max(0, (len(cls._games) - count)) + 1))
            )
        ]

        if colors:
            SCORE_COLUMN = 2
            for row in _rows[1:]:
                row[SCORE_COLUMN] = f"[red]{row[SCORE_COLUMN]}"
            _rows[0][SCORE_COLUMN] = f"[green]{_rows[0][SCORE_COLUMN]}"
        return _rows

    @classmethod
    def live_display(cls) -> Table:
        """Return game stats in a rich.table.Table"""
        cls.countdown = (cls.countdown - 1) % cls.AUTO_SAVE
        cls.save_latest()
        if cls.countdown == 0:
            cls.to_csv(GAME_STATS_FILE_PATH)
        table = Table()
        for header in cls.headers:
            table.add_column(header)

        for row in cls.rows(colors=True):
            table.add_row(*row)
        return table

    @classmethod
    def save_latest(cls):
        yaml_file_name = f"game-history.{len(cls._games)}.yml"
        ascii_file_name = f"game-history.{len(cls._games)}.txt"
        with (GAME_STATS_DIR / ascii_file_name).open("a") as ascii_f, (
            GAME_STATS_DIR / yaml_file_name
        ).open("a") as yaml_f:
            ascii_f.write(cls.full_history[-1].to_ascii() + "\n")
            yaml_f.write(cls.full_history[-1].to_yml() + "\n")

    @classmethod
    def to_csv(cls, filepath: Path) -> None:
        """Save the game statistics table to a CSV file"""
        writer = csv.writer(filepath.open("w"))
        # writer.writerows([cls.headers] + cls.rows(colors=False))
        writer.writerows(cls.rows(colors=False, count=0))
