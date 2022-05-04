from game import Game
from utils import Direction
import random


# Simple example agent that spins in a circle
class SpinnerAgent:
    next_direction = {
        Direction.UP: Direction.RIGHT,
        Direction.RIGHT: Direction.DOWN,
        Direction.DOWN: Direction.LEFT,
        Direction.LEFT: Direction.UP,
    }

    def get_action(self, game: Game):
        return self.next_direction[game.snake.direction]

class RandomAgent:
    ranDirection = random.choice({Direction.UP: Direction.RIGHT,
        Direction.RIGHT: Direction.DOWN,
        Direction.DOWN: Direction.LEFT,
        Direction.LEFT: Direction.UP,})
    
    def get_action(self,game: Game):
        return self.ranDirection[game.snake.direction]

# This is the agent that performs the A*search to get to the pellet
class AStarSearch:
    def get_action(self, game: Game):
        pass


