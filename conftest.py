from typing import Iterable

import pytest

from game import Game
from snake import Snake
from utils import Coordinate


@pytest.fixture
def food():
    """Defines standard food (i.e., starting food is non-random) for testing purposes.

    Changes should be made with caution so as to not break existing tests.
    """

    yield frozenset({Coordinate(3, 3), Coordinate(2, 2)})


@pytest.fixture
def snake():
    """Defines a standard snake instance (i.e., not prone to change) for testing purposes.

    Changes should be made with caution so as to not break existing tests.
    """

    yield Snake(segments=(Coordinate(1, 2), Coordinate(1, 1), Coordinate(2, 1)))


@pytest.fixture
def game(snake, food) -> Iterable[Game]:
    """Defines a standard game instance (i.e., starting food is non-random) for testing purposes.

    Changes should be made with caution so as to not break existing tests.
    """

    game = Game(
        grid_width=5,
        grid_height=5,
        snake=snake,
        food=food,
        score=0,
        ticks=0,
    )

    yield game
