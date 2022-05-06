import csv
import time
from datetime import datetime
from pathlib import Path

from rich.table import Table

from game import Game
from utils import get_timestamped_file_path

DEFAULT_FILE_DIR = Path(__file__).parent / "game-stats"
DEFAULT_FILE_DIR.mkdir(exist_ok=True)
# time stamp for file name is handy for ordering most recent
# it also gives us an easy way to generate meaningful file names with
# low chance of collision
DEFAULT_FILE_PATH = get_timestamped_file_path(dir=DEFAULT_FILE_DIR, suffix=".csv")

while DEFAULT_FILE_PATH.exists():
    # just in case someone starts 2 games at same time
    time.sleep(1)
    DEFAULT_FILE_PATH = (DEFAULT_FILE_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")).with_suffix(
        ".csv"
    )


class GameStats:
    """Utility singleton to help track & display historical stats across games."""

    _games: list[Game] = []
    AUTO_SAVE = countdown = 100
    headers = ("Game #", "Ticks", "Score")

    @classmethod
    def track(cls, game: Game) -> None:
        """Start tracking statistics for a new game."""
        cls._games.append(game)

    @classmethod
    def game_history(cls) -> list[Game]:
        """Get a list of previously played games (oldest at index 0)."""
        return cls._games.copy()

    @classmethod
    def rows(cls, colors: bool = True) -> list[tuple[str, str, str]]:
        """Return rows of game stats.

        Use colors=False for machine-parseable format, True for terminal display.
        """
        rows = []
        score_color = ""
        for i, game in enumerate(cls._games):
            if colors:
                score_color = "[red]" if game.game_over else "[green]"
            rows.append(
                (
                    f"{i+1}",
                    f"{game.ticks}",
                    score_color + f"{game.score}",
                )
            )

        rows.reverse()
        return rows

    @classmethod
    def rich_table(cls) -> Table:
        """Return game stats in a rich.table.Table"""
        cls.countdown = (cls.countdown - 1) % cls.AUTO_SAVE
        if cls.countdown == 0:
            cls.to_csv(DEFAULT_FILE_PATH)
        table = Table()
        for header in cls.headers:
            table.add_column(header)

        for row in cls.rows(colors=True):
            table.add_row(*row)
        return table

    @classmethod
    def to_csv(cls, filepath: Path) -> None:
        """Save the game statistics table to a CSV file"""
        writer = csv.writer(filepath.open("w"))
        writer.writerows([cls.headers] + cls.rows(colors=False))
