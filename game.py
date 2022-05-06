import copy
import logging
import random
from dataclasses import dataclass, field

from snake import Snake
from utils import Coordinate, Direction


@dataclass
class Game:
    grid_width: int
    grid_height: int
    snake: Snake = field(
        default_factory=lambda: Snake(
            segments=[
                Coordinate(0, 1),
                Coordinate(0, 0),
                Coordinate(1, 0),
            ],
            direction=Direction.DOWN,
        )
    )
    food_count: int = 2
    food: set[Coordinate] = field(default_factory=set)
    score: int = 0
    # compare=false because tick is for statistics, not a part
    # of our representation of game state
    ticks: int = field(default=0, compare=False)
    game_over: bool = False

    def __post_init__(self) -> None:
        for _ in range(self.food_count):
            self.spawn_food()

    def __hash__(self):
        return hash(
            (
                self.grid_width,
                self.grid_height,
                tuple(self.snake._segments),
                self.snake.direction,
                frozenset(self.food),
                self.score,
                self.game_over,
            )
        )

    @property
    def successors(self) -> "list[Game]":
        children: "list[Game]" = []
        if self.game_over:
            return children
        for direction in self.snake.direction.next():
            child = copy.deepcopy(self)
            child.update(direction)
            children.append(child)
        return children

    def spawn_food(self) -> None:
        """Adds a new piece of food at a random location.
        Ensures the new food piece doesn't overlap any existing piece.
        """
        new_food = Coordinate(
            random.randrange(0, (self.grid_width - 1)),
            random.randrange(0, (self.grid_height - 1)),
        )

        while new_food in self.food:
            new_food = Coordinate(
                random.randrange(0, (self.grid_width - 1)),
                random.randrange(0, (self.grid_height - 1)),
            )
        logging.debug(f"Spawned {new_food=}")
        self.food.add(new_food)

    def update(self, direction: Direction | None = None) -> None:
        if self.game_over:
            logging.warning(f"Not updating because {self.game_over=}.")
            return
        self.ticks += 1
        logging.debug(f"{self.snake.head=} {self.snake.direction=}")
        if direction is not None:
            self.snake.direction = direction

        if self.snake_eating:
            # snake length increases by 1 and eaten food piece moves to random location
            logging.debug(f"Snake ate food at {self.snake.head=}")
            self.food.remove(self.snake.head)
            self.snake.move(grow=True)
            self.spawn_food()
            self.score += 1
        else:
            # handle the case where we didn't eat (and didn't grow)
            self.snake.move(grow=False)
        self.game_over = self.check_game_over()

    def check_game_over(self) -> bool:
        out_of_bounds = any(
            [
                self.snake.head.X < 0,
                self.snake.head.X > self.grid_width - 1,  # -1 for 0th-index
                self.snake.head.Y < 0,
                self.snake.head.Y > self.grid_height - 1,
            ]
        )
        is_game_over = out_of_bounds or self.snake.ouroboros
        if is_game_over:
            logging.debug(
                f"Game over: {out_of_bounds=} {self.snake.ouroboros=}\n"
                f"{self.snake.head=} {self.snake._segments=}"
            )
        return is_game_over

    @property
    def snake_eating(self) -> Coordinate | None:
        if self.snake.head in self.food:
            return self.snake.head
        return None

    def make_observation(self, action: Direction) -> tuple["Game", float]:
        """Return a simulated action.

        In particular, given a Direction, return the next
        Game state that it would lead to and the score delta*.

        Raises an exception if this state is game_over or action is invalid.
        *Returns -inf in the case that the next state is game_over, the current
        state is game_over, or the action is invalid.
        """
        if self.game_over:
            raise Exception(f"Cannot make observations on a game_over state {self=}")
        if action not in self.snake.direction.next():
            raise Exception(f"Action {action=} is invalid from state {self=}")
        (next_state,) = (s for s in self.successors if s.snake.direction == action)
        score_delta = (
            float("-inf") if next_state.game_over else float(next_state.score - self.score)
        )
        return (next_state, score_delta)
