#!/usr/bin/env python3.10
"""
Snake Eater
Made with PyGame
"""

import logging

from utils import Coordinate, Direction


# Game variables
class Snake:
    _segments: list[Coordinate]
    _direction: Direction

    def __init__(self, segments: list[Coordinate], direction: Direction):
        self._segments = segments
        self._direction = direction

    def move(self, grow: bool):
        if not grow:
            self._segments.pop()

        new_x, new_y = self.head
        if self.direction == Direction.UP:
            new_y -= 1
        elif self.direction == Direction.DOWN:
            new_y += 1
        elif self.direction == Direction.LEFT:
            new_x -= 1
        elif self.direction == Direction.RIGHT:
            new_x += 1
        self._segments.insert(0, Coordinate(X=new_x, Y=new_y))
        logging.debug(f"Snake moved: {grow=} {self.head=}")

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        """Only sets direction if the new value is valid."""
        if value in self.valid_actions:
            self._direction = value
        else:
            logging.debug(
                f"Ignoring invalid action {value=}\n{self.direction=}\n{self.valid_actions=}"
            )

    @property
    def valid_actions(self):
        """Returns the _new_ directions that the snake can _change_ to.

        Based on the snake's current direction."""
        return self.direction.next()

    @property
    def head(self):
        """Return the position of the snake's head."""
        return self._segments[0]

    @head.setter
    def head(self, value):
        self._segments[0] = value

    @property
    def tail(self):
        """Return the position of the snake's tail."""
        return self._segments[-1]

    @tail.setter
    def tail(self, value):
        self._segments[-1] = value

    @property
    def ouroboros(self) -> bool:
        """True iff the snake is eating itself."""
        return self.head in set(self._segments[1:])
