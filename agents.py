import abc
import copy
import logging
import math
from statistics import mean
from typing import Callable, Iterable, NamedTuple

from Algorithm import Algorithm
from game import Game
from snake import Snake
from utils import Direction, Grid, Node, PriorityQueue, manhattan_distance, reciprocal


class BaseAgent(abc.ABC):
    @abc.abstractmethod
    def get_action(self, state: Game) -> Iterable[Direction] | Direction | None:
        ...


def min_man_heuristic(state: Game) -> float:
    """Returns the minimum manhattan distance (from snake head to each food)."""
    return min(manhattan_distance(f, state.snake.head) for f in state.food)


def average_food_heuristic(state: Game) -> float:
    """Return the mean Manhattan distance between snake head and all food."""
    distances_from_head = map(
        lambda food_item: manhattan_distance(state.snake.head, food_item), state.food
    )
    return mean(distances_from_head)


def reciprocal_average_food_heuristic(state: Game) -> float:
    "Returns the reciprocal of ``average_food_heuristic``."
    return reciprocal(average_food_heuristic(state))


class Spinner(BaseAgent):
    """Simple example agent that spins in a circle."""

    next_direction = {
        Direction.UP: Direction.LEFT,
        Direction.LEFT: Direction.DOWN,
        Direction.DOWN: Direction.RIGHT,
        Direction.RIGHT: Direction.UP,
    }

    def get_action(self, game: Game) -> Direction:
        return self.next_direction[game.snake.direction]


class GentleBrute(BaseAgent):
    """Just sweeps the entire game grid repeatedly"""

    def get_action(self, state: Game) -> Direction:
        """
        Snake always starts in top left pointing down. Our strategy looks
        something like this (start in the top left and follow the arrows):

            v<<<<<<<
            v>v>v>v^
            v^v^v^v^
            v^v^v^v^
            >^>^>^>^

        In even columns, the snake moves down, and on odd columns the snake
        moves up. However, we always leave the top row clear for a return to
        start. So, we are always turning when Y=1 or Y=grid_height-1.
        """
        head = state.snake.head
        if head.Y == 0:
            if head.X == 0:
                return Direction.DOWN  # top left corner
            else:
                return Direction.LEFT  # top row
        elif head.Y == 1:
            if head.X == state.grid_width - 1:
                return Direction.UP  # continue to top row if in last column
            elif head.X % 2 == 0:
                return Direction.DOWN  # turning to DOWN in 2nd row
            else:
                return Direction.RIGHT  # turning to RIGHT in 2nd row
        elif head.Y == state.grid_height - 1:
            if head.X % 2 == 0:
                return Direction.RIGHT  # turning to RIGHT in last row
            else:
                return Direction.UP  # turning UP in last row
        elif head.X % 2 == 0:
            return Direction.DOWN  # continue DOWN in even indexed columns
        else:
            return Direction.UP  # continue UP in even indexed columns


class Random(BaseAgent):
    def get_action(self, game: Game) -> Direction:
        return Direction.random()


class TailChaser(BaseAgent):
    def get_action(self, game: Game) -> Iterable[Direction] | None:
        return a_star(
            state=game,
            goal=lambda state: feeder_goal(state) and tail_chaser_goal(state),
        )


class Hungry(BaseAgent):
    def get_action(self, game: Game) -> Iterable[Direction] | None:
        return a_star(state=game, goal=feeder_goal)


class AStarSearch(BaseAgent):
    def get_action(self, game: Game) -> Iterable[Direction]:
        return self.aStarSearch(snake=game.snake, game=game)

    def aStarSearch(
        self,
        snake: Snake,
        game: Game,
        heuristic: Callable[[Game], float] = average_food_heuristic,
    ) -> Iterable[Direction]:
        frontier = PriorityQueue()
        closed_set = []
        frontier.push(([], snake.head, 0), 0)
        while True:
            if frontier.empty:
                return []
            popped = frontier.pop()
            parent_actions: list[Direction] = popped[0]
            parent: Game = popped[1]
            parent_state_cost: float = popped[2]
            if parent not in closed_set:
                if parent.snake_eating:
                    return parent_actions
                closed_set.append(parent)
                children = game.successors
                for child in children:
                    cost = parent_state_cost + 1
                    if child.check_game_over() or parent.check_game_over():
                        cost = float("inf")
                    # state, direction, cost = s
                    child_actions = parent_actions + [child.snake.direction]
                    total = cost + heuristic(child)
                    frontier.push((child_actions, child, cost), total)
                    # hello i am here


def tail_chaser_goal(state: Game) -> bool:
    """Pretend tail is food to find a path, returns True iff snake tail is reachable."""
    copy_state = copy.deepcopy(state)
    copy_state.food = {copy_state.snake.tail}
    return a_star(copy_state, goal=feeder_goal) is not None


def feeder_goal(state: Game) -> bool:
    """Return True iff snake's head is at the same location as a piece of food."""
    return state.snake_eating is not None


def a_star(
    state: Game,
    heuristic: Callable[[Game], float] = min_man_heuristic,
    goal: Callable[[Game], bool] = lambda state: feeder_goal(state) and tail_chaser_goal(state),
) -> tuple[Direction, ...] | None:
    heuristic_warning = False
    closed = []
    frontier = PriorityQueue()
    frontier.push(item=PathNode(actions=(), state=state, cost=0), priority=0)
    while frontier.has_items:
        current_node: PathNode = frontier.pop()
        logging.debug(
            f"A* EVALUATING:\n"
            f"\thead={current_node.state.snake.head} food={current_node.state.food}\n"
            f"\tcost={current_node.cost} actions={current_node.actions}"
        )
        if goal(current_node.state):
            logging.debug(f"A* GOAL: {current_node=}")
            return current_node.actions
        closed.append(current_node.state)
        successor_nodes = [
            PathNode(
                cost=current_node.cost + 1,
                actions=current_node.actions + (successor_state.snake.direction,),
                state=successor_state,
            )
            for successor_state in current_node.state.successors
        ]
        for successor_node in successor_nodes:
            heuristic_value: float = heuristic(successor_node.state)
            if successor_node in frontier and successor_node.cost < heuristic_value:
                # remove successor from frontier, because new path is better
                frontier.remove(item=successor_node)

            if successor_node.state in closed and successor_node.cost < heuristic_value:
                if not heuristic_warning:
                    logging.warning(f"Inadmissible: {heuristic_value=} < {successor_node.cost=}")
                    logging.debug(f"Inadmissible heuristic was evaluating: {successor_node=}")
                    heuristic_warning = True
                closed.remove(successor_node.state)  # remove successor from closed
            if successor_node not in frontier and successor_node.state not in closed:
                logging.debug(
                    f"A* PUSHING:\n"
                    f"\thead={successor_node.state.snake.head} food={successor_node.state.food}\n"
                    f"\tcost={successor_node.cost} actions={successor_node.actions}"
                )
                frontier.push(item=successor_node, priority=successor_node.cost + heuristic_value)

    return None  # no path to goal state


class PathNode(NamedTuple):
    """Utility class to represent a node in a search path.

    PathNode is just a wrapper around Game states allowing us to associate a reverse
    a path from start to the state and the cost of getting there.
    """

    actions: tuple[Direction, ...]
    state: Game
    cost: float


class DFS(Algorithm):
    def __init__(self, grid):
        super().__init__(self, grid)

    def recursive_DFS(self, snake: Snake, goalstate, currentstate):
        # check if goal state
        if currentstate == goalstate:
            return self.get_path(currentstate)

        # if already visted return
        if currentstate in self.explored_set:
            return None

        self.explored_set.append(currentstate)  # mark visited
        neighbors = self.get_neighbors(currentstate)  # get neighbors

        # for each neighbor
        for neighbor in neighbors:
            if not self.inside_body(snake, neighbor) and neighbor not in self.explored_set:
                neighbor.parent = currentstate  # mark parent node
                path = self.recursive_DFS(snake, goalstate, neighbor)  # check neighbor
                if path != None:
                    return path  # found path
        return None

    def run_algorithm(self, snake):
        # to avoid looping in the same location
        if len(self.path) != 0:
            # while you have path keep going
            path = self.path.pop()

            if self.inside_body(snake, path):
                self.path = []  # or calculate new path!
            else:
                return path

        # start clean
        self.frontier = []
        self.explored_set = []
        self.path = []

        initialstate, goalstate = self.get_initstate_and_goalstate(snake)

        self.frontier.append(initialstate)

        # return path
        return self.recursive_DFS(snake, goalstate, initialstate)
