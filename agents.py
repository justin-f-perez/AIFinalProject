from game import Game
from utils import Direction


class SpinnerAgent:
    next_direction = {
        Direction.UP: Direction.RIGHT,
        Direction.RIGHT: Direction.DOWN,
        Direction.DOWN: Direction.LEFT,
        Direction.LEFT: Direction.UP,
    }

    def get_action(self, game: Game):
        return self.next_direction[game.snake.direction]
