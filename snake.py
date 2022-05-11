#!/usr/bin/env python3.10
"""
Snake Eater
Made with PyGame
"""

import logging
from dataclasses import dataclass

from serializers import SerializerMixin
from utils import Coordinate, Direction


@dataclass(frozen=True, eq=True, order=True, kw_only=True, slots=True)
class Snake(SerializerMixin):
    segments: tuple[Coordinate, ...] = (
        Coordinate(0, 1),
        Coordinate(0, 0),
        Coordinate(1, 0),
    )

    def validate_segments(self) -> bool:
        if len(self.segments) < 2:
            # 2 because we depend on the 2nd segment to find direction
            return False
        for previous, next in zip(self.segments[:-1], self.segments[1:]):
            if abs(previous.X - next.X) + abs(previous.Y - next.Y) != 1:
                return False
        return True

    @property
    def valid_actions(self) -> set[Direction]:
        """Returns the _new_ directions that the snake can _change_ to.

        Based on the snake's current direction."""
        directions: set[Direction] = self.direction.next()
        return directions

    @property
    def ouroboros(self) -> bool:
        """True iff the snake is eating itself."""
        return self.head in self.segments[1:]

    @property
    def direction(self) -> Direction:
        if len(self.segments) == 1:
            return Direction.random()
        # fmt: off
        match (self.head.X - self.neck.X, self.head.Y - self.neck.Y):
            case (-1, 0): return Direction.LEFT
            case (1, 0): return Direction.RIGHT
            case (0, 1): return Direction.DOWN
            case (0, -1): return Direction.UP
            case _: raise Exception()
        # fmt: on

    @property
    def head(self) -> Coordinate:
        """Return the position of the snake's head."""
        return self.segments[0]

    @property
    def tail(self) -> Coordinate:
        """Return the position of the snake's tail."""
        return self.segments[-1]

    @property
    def neck(self) -> Coordinate:
        """Return the element at index 1"""
        # we use this for finding direction
        try:
            return self.segments[1]
        except IndexError:
            raise Exception(
                f"Attempted to access snake.neck, but the snake is too short! {self.segments=}"
            )

    def move(self, direction: Direction | None, grow: bool) -> "Snake":
        if direction is None:
            direction = self.direction
        if direction not in self.valid_actions:
            raise Exception(f"Invalid movement direction {direction=}")
        new_x, new_y = self.head
        match direction:
            case Direction.UP:
                new_y -= 1
            case Direction.DOWN:
                new_y += 1
            case Direction.LEFT:
                new_x -= 1
            case Direction.RIGHT:
                new_x += 1

        logging.debug(f"Snake moved: {grow=} {self.head=}")
        new_head = Coordinate(X=new_x, Y=new_y)
        new_body = self.segments[:] if grow else self.segments[:-1]
        return Snake(segments=(new_head,) + new_body)
