import enum
import heapq
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, NamedTuple

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


class Node:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.h = 0
        self.g = 0
        self.f = 1000000
        self.parent = None

    def print(self):
        print(f"x: {self.x} y: {self.y}")

    def equal(self, b):
        return self.x == b.x and self.y == b.y


class Grid:
    def __init__(self):
        self.grid = []

        for i in range(20):
            col = []
            for j in range(20):
                col.append(Node(i, j))
            self.grid.append(col)


def arg_max(
    iterable: Iterable[Any],
    func: Callable[[Any], Any],
    break_ties: Callable[[Any], Any] = random.choice,
) -> Any:
    """Return the item in `iterable` that maximizes `func`."""
    best_items = []
    best_value = float("-inf")
    for item in iterable:
        item_value = func(item)
        if item_value == best_value:
            best_items.append(item)
        elif item_value > best_value:
            best_value = item_value
            best_items = [item]
    return break_ties(best_items) if len(best_items) else None


def timestamp() -> str:
    "Returns a timestamp in YYYYMMDD_HHMMSS (i.e., <DATE>_<TIME>) format"
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_timestamped_file_path(dir: Path, suffix: str) -> Path:
    """Given a directory and suffix, returns a Path to a file whose name represents current time.

    If file already exists, this funcdtion will sleep for 1 second and retry 3 times before raising
    an exception.
    """
    file_path = (dir / timestamp()).with_suffix(suffix)

    retries = 3
    while file_path.exists():
        retries -= 1
        if retries < 0:
            raise Exception(f"File already exists (3rd retry) {file_path}")
        # just in case someone starts 2 games at same time
        time.sleep(1)
        file_path = (dir / timestamp()).with_suffix(".csv")

    return file_path
