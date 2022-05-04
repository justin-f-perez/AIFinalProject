import enum
from typing import NamedTuple

import pygame


class Color(enum.Enum):
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)
    RED = pygame.Color(255, 0, 0)
    GREEN = pygame.Color(0, 255, 0)
    BLUE = pygame.Color(0, 0, 255)


class Direction(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()

    def next(self):
        """Return next valid actions from the given action."""
        valid = {
            Direction.UP: {Direction.LEFT, Direction.RIGHT},
            Direction.DOWN: {Direction.LEFT, Direction.RIGHT},
            Direction.LEFT: {Direction.UP, Direction.DOWN},
            Direction.RIGHT: {Direction.UP, Direction.DOWN},
        }
        return valid[self]


class Coordinate(NamedTuple):
    X: int
    Y: int
