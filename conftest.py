from typing import Iterable

import pytest

from game import Game
from snake import Snake
from utils import Coordinate, Direction


@pytest.fixture
def game() -> Iterable[Game]:
    snake = Snake(
        segments=[Coordinate(1, 1), Coordinate(1, 0), Coordinate(0, 0)],
        direction=Direction.DOWN,
    )
    game = Game(
        food_count=2,
        grid_width=100,
        grid_height=100,
        snake=snake,
    )
    yield game
