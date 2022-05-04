import abc
import importlib
import sys

import pygame

from game import Game
from utils import Direction
from views import GameView, HeadlessGameView


class Controller(abc.ABC):
    def __init__(self, game: Game, game_view: GameView, frame_rate=0):
        self.game = game
        self.clock = pygame.time.Clock()
        self.game_view = game_view
        self.frame_rate = frame_rate

    @abc.abstractmethod
    def get_action(self) -> Direction | None:
        ...

    def run(self):
        while True:
            self.game.update(self.get_action())
            self.game_view.update()
            self.clock.tick(self.frame_rate)


class Keyboard(Controller):
    def get_action(self) -> Direction | None:
        direction = None
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # ESC = Quit
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # W=Up; S=Down; A=Left; D=Right
                key_map = {
                    pygame.K_UP: Direction.UP,
                    ord("w"): Direction.UP,
                    pygame.K_LEFT: Direction.LEFT,
                    ord("a"): Direction.LEFT,
                    pygame.K_DOWN: Direction.DOWN,
                    ord("s"): Direction.DOWN,
                    pygame.K_RIGHT: Direction.RIGHT,
                    ord("d"): Direction.RIGHT,
                }
                direction = key_map[event.key]
        return direction


class Agent(Controller):
    def __init__(
        self,
        agent_class,
        agent_args=(),
        agent_kwargs=None,
        game_view: GameView = None,
        *args,
        **kwargs,
    ):
        """Same init logic as Controller base class, but...

        * provides a default headless game view
        * accepts arguments for initializing an AI agent:
            * agent_class: should be a class or python module path, e.g., "agents.SpinnerAgent"
            * agent_args: an iterable of positional arguments to pass to the agent
            * agent_args: an mapping of keyword arguments to pass to the agent
        * Agent class given by agent_class should implement a get_action(self, game) method
            that returns either a single action or list of actions.
        """
        super().__init__(game_view=game_view or HeadlessGameView(), *args, **kwargs)  # type: ignore
        if isinstance(agent_class, str):
            try:
                AgentClass = importlib.import_module(agent_class)
            except ModuleNotFoundError:
                module_path, class_name = (
                    ".".join((parts := agent_class.split("."))[:-1]),
                    parts[-1],
                )
                AgentModule = importlib.import_module(module_path)
                AgentClass = getattr(AgentModule, class_name)
        else:
            AgentClass = agent_class
        if agent_kwargs is None:
            agent_kwargs = {}
        self.agent_instance = AgentClass(*agent_args, **agent_kwargs)  # type: ignore
        self.actions: list[Direction] = []

    def get_action(self):
        if self.actions:
            # if we previously got a list of actions from the agent, use those first
            return self.actions.pop(0)

        # for some reason game window doesn't render if we don't consume the event queue
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # ESC = Quit
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        action_list_or_action = self.agent_instance.get_action(self.game)

        # if it's just one
        if isinstance(action_list_or_action, Direction):
            return action_list_or_action
        else:  # actions (plural); store to consume as a queue
            self.actions = action_list_or_action
