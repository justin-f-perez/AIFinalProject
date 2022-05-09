"""
State transformers are wrappers around Game model states.
"""

import operator
from dataclasses import dataclass
from typing import Iterable

from game import Game
from snake import Snake
from utils import Coordinate, Direction


@dataclass(frozen=True, eq=True, order=True, kw_only=True, slots=True)
class ObstacleFoodDirectionState:
    game: Game

    def check_dir(self, to: Iterable[Coordinate] | Coordinate, dir: Direction) -> bool:
        from_ = self.game.snake.head

        def _check(to, dir, from_):
            op = operator.lt if dir in (Direction.LEFT, Direction.UP) else operator.gt
            attr = "X" if Direction in (Direction.LEFT, Direction.RIGHT) else "Y"
            return op(getattr(to, attr), getattr(from_, attr))

        if isinstance(to, Coordinate):
            return _check(to, dir, from_)
        else:
            return any(_check(t, dir, from_) for t in to)

    @property
    def food(self) -> frozenset[Coordinate]:
        return self.game.food

    @property
    def snake(self) -> Snake:
        return self.game.snake

    @property
    def food_left(self) -> bool:
        return self.check_dir(to=self.game.food, dir=Direction.LEFT)

    @property
    def food_right(self) -> bool:
        return self.check_dir(to=self.game.food, dir=Direction.RIGHT)

    @property
    def food_up(self) -> bool:
        return self.check_dir(to=self.game.food, dir=Direction.UP)

    @property
    def food_down(self) -> bool:
        return self.check_dir(to=self.game.food, dir=Direction.DOWN)

    @property
    def obstacle_left(self) -> bool:
        return self.check_dir(to=self.game.snake.segments, dir=Direction.LEFT)

    @property
    def obstacle_right(self) -> bool:
        return self.check_dir(to=self.game.snake.segments, dir=Direction.RIGHT)

    @property
    def obstacle_up(self) -> bool:
        return self.check_dir(to=self.game.snake.segments, dir=Direction.UP)

    @property
    def obstacle_down(self) -> bool:
        return self.check_dir(to=self.game.snake.segments, dir=Direction.DOWN)


def obstacle_food_direction_state(game: Game):
    """Returns a tuple (FL, FR, FU, FD, OL, OR, OU, OD) constructed from game state.

    Notation:
        F = Food, O = Obstacle
        L = Left, R = Right, U = Up, D = Down

        e.g., FL = "Food Left"
    """

    def check_dir(to: Iterable[Coordinate] | Coordinate, dir: Direction) -> bool:
        # outter func generalizes to multiple "to" coordinates
        def _check(to, dir):  # inner func checks single coordinate
            op = operator.lt if dir in (Direction.LEFT, Direction.UP) else operator.gt
            attr = "X" if Direction in (Direction.LEFT, Direction.RIGHT) else "Y"
            return op(getattr(to, attr), getattr(game.snake.head, attr))

        if isinstance(to, Coordinate):
            return _check(to, dir)
        else:
            return any(_check(t, dir) for t in to)

    return (
        check_dir(to=game.food, dir=Direction.LEFT),
        check_dir(to=game.food, dir=Direction.RIGHT),
        check_dir(to=game.food, dir=Direction.UP),
        check_dir(to=game.food, dir=Direction.DOWN),
        check_dir(to=game.snake.segments, dir=Direction.LEFT),
        check_dir(to=game.snake.segments, dir=Direction.RIGHT),
        check_dir(to=game.snake.segments, dir=Direction.UP),
        check_dir(to=game.snake.segments, dir=Direction.DOWN),
    )
