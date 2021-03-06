import abc
import logging
import random
from dataclasses import dataclass, field, replace
from pprint import pprint
from statistics import mean
from typing import Any, Callable, Iterable, NamedTuple

from game import Game
from transformers import obstacle_food_direction_state
from utils import (
    Direction,
    PriorityQueue,
    arg_max,
    get_timestamped_file_path,
    manhattan_distance,
    reciprocal,
)


class BaseAgent(abc.ABC):
    @abc.abstractmethod
    def get_action(self, state: Game) -> Iterable[Direction] | Direction | None:
        ...


def min_man_heuristic(state: Game) -> float:
    """Returns the minimum manhattan distance (from snake head to each food)."""
    if state.game_over:
        return float("-inf")
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
        return a_star2(
            state=game,
            goal=lambda state: feeder_goal(state) and tail_chaser_goal(state),
        )


class Hungry(BaseAgent):
    def get_action(self, game: Game) -> Iterable[Direction] | None:
        return a_star2(state=game, goal=feeder_goal)


def tail_chaser_goal(state: Game) -> bool:
    """Pretend tail is food to find a path, returns True iff snake tail is reachable."""
    tail_goal_state: Game = replace(state, food=frozenset([state.snake.tail]))
    return a_star(tail_goal_state, goal=feeder_goal) is not None


def feeder_goal(state: Game) -> bool:
    """Return True iff snake's head is at the same location as a piece of food."""
    return len(state.food_at(state.snake.head)) > 0


def a_star2(
    state: Game,
    heuristic: Callable[[Game], float] = min_man_heuristic,
    goal: Callable[[Game], bool] = lambda state: feeder_goal(state) and tail_chaser_goal(state),
) -> tuple[Direction, ...] | None:
    heuristic_warning = False
    closed = []
    frontier = PriorityQueue()
    # frontier.push(item=PathNode(actions=(), state=state, cost=0), priority=0)
    successor_nodes = [
        PathNode(
            cost=1,
            actions=(successor_state.snake.direction,),
            state=successor_state,
        )
        for successor_state in state.successors
        if not successor_state.game_over
    ]
    for successor_node in successor_nodes:
        frontier.push(
            item=successor_node, priority=successor_node.cost + heuristic(successor_node.state)
        )

    while frontier.has_items:
        current_node: PathNode = frontier.pop()
        logging.debug(
            f"A* EVALUATING:\n"
            f"\thead={current_node.state.snake.head} food={current_node.state.food}\n"
            f"\tcost={current_node.cost} actions={current_node.actions}"
        )
        if goal(current_node.state):
            logging.debug(f"A* GOAL {goal=} FOUND: {current_node=}")
            return current_node.actions
        closed.append(current_node.state.snake.head)
        successor_nodes = [
            PathNode(
                cost=current_node.cost + 1,
                actions=current_node.actions + (successor_state.snake.direction,),
                state=successor_state,
            )
            for successor_state in current_node.state.successors
            if not successor_state.game_over
        ]
        for successor_node in successor_nodes:
            heuristic_value: float = heuristic(successor_node.state)
            if successor_node in frontier and successor_node.cost < heuristic_value:
                # remove successor from frontier, because new path is better
                frontier.remove(item=successor_node)

            if successor_node.state.snake.head in closed and successor_node.cost < heuristic_value:
                if not heuristic_warning:
                    logging.warning(f"Inadmissible: {heuristic_value=} < {successor_node.cost=}")
                    logging.debug(f"Inadmissible heuristic was evaluating: {successor_node=}")
                    heuristic_warning = True
                closed.remove(successor_node.state.snake.head)  # remove successor from closed
            if successor_node not in frontier and successor_node.state.snake.head not in closed:
                logging.debug(
                    f"A* PUSHING:\n"
                    f"\thead={successor_node.state.snake.head} food={successor_node.state.food}\n"
                    f"\tcost={successor_node.cost} actions={successor_node.actions}"
                )
                frontier.update(item=successor_node, priority=successor_node.cost + heuristic_value)

    return None  # no path to goal state


def a_star(
    state: Game,
    heuristic: Callable[[Game], float] = min_man_heuristic,
    goal: Callable[[Game], bool] = lambda state: feeder_goal(state) and tail_chaser_goal(state),
) -> tuple[Direction, ...] | None:
    heuristic_warning = False
    closed = []
    frontier = PriorityQueue()
    # frontier.push(item=PathNode(actions=(), state=state, cost=0), priority=0)
    successor_nodes = [
        PathNode(
            cost=1,
            actions=(successor_state.snake.direction,),
            state=successor_state,
        )
        for successor_state in state.successors
        if not successor_state.game_over
    ]
    for successor_node in successor_nodes:
        frontier.push(
            item=successor_node, priority=successor_node.cost + heuristic(successor_node.state)
        )

    while frontier.has_items:
        current_node: PathNode = frontier.pop()
        logging.debug(
            f"A* EVALUATING:\n"
            f"\thead={current_node.state.snake.head} food={current_node.state.food}\n"
            f"\tcost={current_node.cost} actions={current_node.actions}"
        )
        if goal(current_node.state):
            logging.debug(f"A* GOAL {goal=} FOUND: {current_node=}")
            return current_node.actions
        closed.append(current_node.state)
        successor_nodes = [
            PathNode(
                cost=current_node.cost + 1,
                actions=current_node.actions + (successor_state.snake.direction,),
                state=successor_state,
            )
            for successor_state in current_node.state.successors
            if not successor_state.game_over
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
                frontier.update(item=successor_node, priority=successor_node.cost + heuristic_value)

    return None  # no path to goal state


class PathNode(NamedTuple):
    """Utility class to represent a node in a search path.

    PathNode is just a wrapper around Game states allowing us to associate a reverse
    a path from start to the state and the cost of getting there.
    """

    actions: tuple[Direction, ...]
    state: Game
    cost: float


QValues = dict[tuple[Game | tuple, Direction], float]  # type variable


@dataclass
class QQ(BaseAgent):
    """A Q-learning agent.

    For more information about Q-learning:
        https://en.wikipedia.org/wiki/Q-learning

    Q:
        the dictionary mapping (state,action) pairs to a Q-value
    learning_rate:
        the learning rate. Higher learning rates cause Q-values to change faster.
    learning_rate_decay:
        a decay factor applied each time ``get_action()`` is called. Use 1.0 to disable.
    discount:
        aka "??" or "gamma", a "temporal decay" factor on future rewards (by scaling Q-values).
        Use 1.0 to disable.
        For example, suppose you have a graph where the initial state is A, goal state is B,
        and there are two paths from A to B:
            Path 1: A -> B
            Path 2: A -> C -> D -> B
        With a discount, Path 1 would be more valuable than Path 2. The difference in these
        values becomes greater as discount approaches 0 from 1.
    dump: whether or not to dump q values to a .qvals file in the debug-log directory
    exploration_rate: the exploration rate. See: ``get_action``
    """

    state_transformer: Callable[[Game], tuple[Any, ...]] = field(
        default=obstacle_food_direction_state
    )
    Q: QValues = field(default_factory=dict)
    learning_rate: float = 1.0
    learning_rate_decay: float = 0.999
    discount: float = 0.99
    dump: bool = True
    exploration_rate: float = 0.5
    exploration_rate_decay: float = 0.999
    living_reward: float = -0.01

    def __post_init__(self):
        if self.dump:
            self.dump_file = get_timestamped_file_path("debug-logs", suffix=".q").open("w")

    def get_action(self, state: Game) -> Iterable[Direction] | Direction | None:
        """Returns the appropriate action to take for the given ``state``.

        The appropriate action depends on the learned Q values and the exploration rate.
        With probability(self.exploration_rate), a random action is chosen; otherwise the best
        action (as given by the learned Q values is returned).
        """
        self.learning_rate *= self.learning_rate_decay
        self.exploration_rate *= self.exploration_rate_decay
        if random.random() <= self.exploration_rate:
            action = random.choice(list(state.snake.direction.next()))
        else:
            action = self.get_learned_action(state)
        next_state, reward = state.make_observation(action)
        self.update(state, action, next_state, reward + self.living_reward)

        if self.dump:
            self.dump_file.seek(0)
            self.dump_file.truncate(0)
            pprint(self.Q, stream=self.dump_file)
            # self.dump_file.write(str(self.Q))
        return action

    def get_Q_value(self, state: Game, action: Direction) -> float:
        """Return Q(s,a), or 0.0 if a state has never been seen."""
        try:
            return self.Q.get((self.state_transformer(state), action), 0.0)
        except Exception:
            logging.exception(f"{state=}")
            raise

    def get_value(self, state: Game) -> float:
        """Return max(Q(s,a) for a in legal actions), or 0.0 when no actions."""
        q_values = [self.get_Q_value(state, a) for a in state.snake.direction.next()]
        return max(q_values) if q_values else 0.0

    def get_learned_action(self, state: Game) -> Direction:
        actions = state.snake.direction.next()
        return arg_max(actions, lambda action: self.get_Q_value(state, action))

    def difference(self, state: Game, action: Direction, next_state: Game, reward: float) -> float:
        r"""Return the discounted V(s2) + reward - Q(s,a)"""
        Qsa, V = self.get_Q_value(state, action), self.get_value(next_state)
        return reward + self.discount * V - Qsa

    def update(self, state: Game, action: Direction, next_state: Game, reward: float) -> None:
        """Learn a new transition."""
        weighted_difference = self.learning_rate * self.difference(
            state, action, next_state, reward
        )
        self.Q[(self.state_transformer(state), action)] = (
            self.get_Q_value(state, action) + weighted_difference
        )
        if random.random() < 0.01:
            # we just occassionally log Q values 1% of the time so the log file doesn't get too big
            logging.debug(f"Q update: {self.Q.values()}")
