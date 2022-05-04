from game import Game
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


# This is the agent that performs the A*search to get to the pellet
class aStarSearch:
    def get_action(self, game: Game):
        pass

    def aStarSearch(snake, game, heuristic):
        frontier = PriorityQueue()
        closedSet = set()
        frontier.push(([], snake.head(), 0), 0)
        while True:
            if frontier.isEmpty():
                return None
            lActions, curNode, currcost = frontier.pop()
            if game.isGoalState(curNode):
                return lActions
            if curNode not in closedSet:
                closedSet.add(curNode)
                successors = game.getSuccessors(curNode)
                for successor in successors:
                    state, direction, cost = successor
                    nListActions = lActions + [direction]
                    total = currcost + cost + heuristic(state, snake)
                    frontier.push((nListActions, state, currcost + cost), total)
