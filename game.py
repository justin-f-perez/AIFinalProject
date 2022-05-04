
   
import logging
import random
from dataclasses import dataclass, field

from snake import Snake
from utils import Coordinate


@dataclass
class Game:
    grid_width: int
    grid_height: int
    snake: Snake
    food_count: int
    food: set[Coordinate] = field(default_factory=set)
    score: int = 0
    game_over: bool = False

    def __post_init__(self):
        for _ in range(self.food_count):
            self.spawn_food()

    def spawn_food(self):
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

    def update(self, direction=None):
        logging.debug(f"{self.snake.head=} {self.snake.direction=}")
        if direction is not None:
            self.snake.direction = direction

        if self.snake.head in self.food:
            # snake length increases by 1 and eaten food piece moves to random location
            logging.debug(f"Snake ate food at {self.snake.head=}")
            self.food.remove(self.snake.head)
            self.snake.move(grow=True)
            self.spawn_food()
            self.score += 1
        else:
            # handle the case where we didn't eat, and didn't grow
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

    # IMPLEMENT A ISGOALSTATE METHOD
    def isGoalState(self):
        if self.snake.head in self.food: return True 
        else :return False 

