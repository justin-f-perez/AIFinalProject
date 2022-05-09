import logging
from dataclasses import dataclass, field, replace

from serializers import SerializerMixin
from snake import Snake
from utils import Coordinate, Direction


@dataclass(frozen=True, eq=True, order=True, kw_only=True, slots=True)
class Game(SerializerMixin):
    grid_width: int = 5
    grid_height: int = 5
    snake: Snake = field(
        default_factory=lambda: Snake(
            segments=(
                Coordinate(0, 1),
                Coordinate(0, 0),
                Coordinate(1, 0),
            ),
        )
    )
    food: frozenset[Coordinate] = field(
        default_factory=lambda: Coordinate.random(grid_height=5, grid_width=5, n=2)
    )
    score: int = 0
    # compare=false because tick is for statistics, not a part
    # of our representation of game state
    ticks: int = field(default=0, compare=False)

    def to_ascii(self):
        FOOD_SYMBOL = "🍎"
        BLANK_SYMBOL = "🔵"
        SNAKE_SYMBOL = "🐍"
        horizontal_border_row = ["☰" for _ in range(int((self.grid_width) * 2 + 2))]
        grid_row = ["║"] + [BLANK_SYMBOL for _ in range(self.grid_width)] + ["║"]
        grid = [grid_row.copy() for _ in range(self.grid_height)]
        grid.insert(0, horizontal_border_row)
        grid.append(horizontal_border_row)

        try:
            for s in self.snake.segments:
                grid[s.Y + 1][s.X + 1] = SNAKE_SYMBOL
        except Exception as ex:
            logging.error(self.to_yaml())
            logging.error(f"Bad segment: {s=}")
            logging.exception(ex)
            raise

        try:
            for f in self.food:
                grid[f.Y + 1][f.X + 1] = FOOD_SYMBOL
        except Exception as ex:
            logging.error(self.to_yaml())
            logging.error(f"Bad food: {f=}")
            logging.exception(ex)
            raise

        return "\n".join("".join(line) for line in grid)

    @property
    def game_over(self) -> bool:
        return self._check_game_over()

    @property
    def successors(self) -> "list[Game]":
        children: "list[Game]" = []
        if self.game_over:
            return children
        return [self.update(direction) for direction in self.snake.direction.next()]

    def spawn_food(self) -> frozenset["Coordinate"]:
        """Adds a new piece of food at a random location.
        Ensures the new food piece doesn't overlap any existing piece.
        """
        return Coordinate.random(
            exclude=self.food, grid_width=self.grid_width, grid_height=self.grid_height, n=1
        )

    def update(self, direction: Direction | None = None) -> "Game":
        if self.game_over:
            raise Exception(f"Can't update a game when {self.game_over=}.")

        eating = self.food_at(self.snake.head)
        new_food = (frozenset(self.food) - eating) | (self.spawn_food() if eating else frozenset())
        new_snake = self.snake.move(direction=direction, grow=len(eating) > 0)
        new_state_changes = {
            "ticks": self.ticks + 1,
            "snake": new_snake,
            "food": new_food,
            "score": self.score + len(eating),
        }

        new_state = replace(self, **new_state_changes)
        logging.debug(f"STATE TRANSITION:\n{self}\n\t-\n\t\t{new_state}")
        return new_state

    def _check_game_over(self) -> bool:
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
                f"{self.snake.head=} {self.snake.segments=}"
            )
        return is_game_over

    def food_at(self, coordinate: Coordinate) -> frozenset[Coordinate]:
        return frozenset({coordinate}) & self.food

    def make_observation(self, action: Direction | None) -> tuple["Game", float]:
        """Return a simulated action.

        In particular, given a Direction, return the next
        Game state that it would lead to and the score delta*.

        Raises an exception if this state is game_over or action is invalid.
        *Returns -1 in the case that the next state is game_over.
        """
        action = action or self.snake.direction
        if self.game_over:
            raise Exception(f"Cannot make observations on a game_over state {self=}")
        if action not in self.snake.direction.next():
            raise Exception(f"Action {action=} is invalid from state {self=}")
        (next_state,) = (s for s in self.successors if s.snake.direction == action)
        score_delta = float(-1) if next_state.game_over else float(next_state.score - self.score)
        return (next_state, score_delta)
