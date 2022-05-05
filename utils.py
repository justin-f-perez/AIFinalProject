import enum
import heapq
import random
from dataclasses import dataclass, field
from typing import Any, NamedTuple

import pygame


def reciprocal(num: float) -> float:
    if num == 0:
        return float("inf")
    return 1 / num


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

    @classmethod
    def random(cls) -> "Direction":
        return random.choice(list(cls))

    def next(self) -> set["Direction"]:
        """Return next valid actions from the given action."""
        valid = {
            Direction.UP: {Direction.LEFT, Direction.RIGHT, Direction.UP},
            Direction.DOWN: {Direction.LEFT, Direction.RIGHT, Direction.DOWN},
            Direction.LEFT: {Direction.UP, Direction.DOWN, Direction.LEFT},
            Direction.RIGHT: {Direction.UP, Direction.DOWN, Direction.RIGHT},
        }
        return valid[self]


@dataclass(order=True)
class PrioritizedItem:
    """Helper class for PriorityQueue."""

    priority: float
    # we disable comparison on the item so unorderable objects, like ``Direction``s
    # don't cause errors from heapq trying to order them
    item: Any = field(compare=False)


# Priority queue class is from the pacman game util.py used in class...
class PriorityQueue:
    """A priority queue which pops the smallest items first."""

    def __init__(self) -> None:
        self.heap: list[PrioritizedItem] = []

    def __str__(self) -> str:
        return str(self.heap)

    def __repr__(self) -> str:
        return repr(self.heap)

    def __contains__(self, item: Any) -> bool:
        """Return True if the item exists in the ``PriorityQueue`` (priority is ignored)."""
        for prioritized_item in self.heap:
            if prioritized_item.item == item:
                return True
        return False

    def remove(self, item: Any) -> None:
        """Remove ``item`` from the priority queue.

        An error is thrown if the item does not exist.
        If ``item`` is repeated in the ``PriorityQueue``, it is only removed once.
        """
        for index, entry in enumerate(self.heap):
            if entry.item == item:
                del self.heap[index]
                heapq.heapify(self.heap)

    def push(self, item: Any, priority: float) -> None:
        """Add an ``item`` to the ``PriorityQueue`` with the given ``priority``"""
        entry = PrioritizedItem(priority=priority, item=item)
        heapq.heappush(self.heap, entry)

    def pop(self) -> Any:
        """Return (and remove) the ``item`` with the lowest ``priority`` value."""
        return heapq.heappop(self.heap).item

    @property
    def empty(self) -> bool:
        """True iff the heap underlying the ``PriorityQueue`` is empty."""
        return len(self.heap) == 0

    @property
    def has_items(self) -> bool:
        """True iff there are elements in the ``PriorityQueue``."""
        return not self.empty

    def update(self, item: Any, priority: float) -> None:
        """Adds or updates the priority of ``item`` within the PriorityQueue.

        If the ``item`` already exists, its ``priority`` is updated. Otherwise,
        ``item`` is added to the ``PriorityQueue`` with the given ``priority``.
        """
        self.remove(item)
        self.push(item, priority)


class Coordinate(NamedTuple):
    X: int
    Y: int


def manhattan_distance(xy1: tuple[int, int], xy2: tuple[int, int]) -> int:
    "Returns the Manhattan distance between points xy1 and xy2"
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
