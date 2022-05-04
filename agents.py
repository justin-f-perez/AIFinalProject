import random

from game import Game
from snake import Snake
from utils import Direction, PriorityQueue


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


class RandomAent:
    ranDirection = random.choice(
        [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
    )

    def get_action(self, game: Game):
        return self.ranDirection


# Heuristic function ---
def manhattanDistance(xy1, xy2):
    "Returns the Manhattan distance between points xy1 and xy2"
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


# Identify tail position and see if it is reachable.
# Keep track of where the wall is
# Give negative points for above two ^

# This is the agent that performs the A*search to get to the pellet
class aStarSearch:
    def get_action(self, game: Game):
        actionList = self.aStarSearch(game.snake, game)
        return actionList

    def aStarSearch(self, snake: Snake, game: Game, heuristic=manhattanDistance):
        frontier = PriorityQueue()
        closedSet = set()
        frontier.push(([], snake.head, 0), 0)
        while True:
            if frontier.isEmpty():
                return None
            lActions, curNode, currcost = frontier.pop()
            if game.isGoalState():
                return lActions
            if curNode not in closedSet:
                closedSet.add(curNode)
                success = game.successors
                for s in success:
                    state, direction, cost = s
                    nListActions = lActions + [direction]
                    total = currcost + cost + heuristic(state, snake)
                    frontier.push((nListActions, state, currcost + cost), total)
                    # hello i am here
