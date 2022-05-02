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


class Coordinate(NamedTuple):
    X: int
    Y: int
