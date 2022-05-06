import abc
import copy
import importlib
import sys
import time
from typing import Any, Iterable, Mapping, TypeVar

import pygame
from rich.live import Live

from agents import BaseAgent
from game import Game
from stats import GameStats
from utils import Direction
from views import GameView, GraphicsGameView, HeadlessGameView


class Controller(abc.ABC):
    def __init__(
        self,
        game: Game,
        game_view: GameView,
        frame_rate: int = 0,
        auto_restart: bool = False,
        harvest: int | None = None,
    ) -> None:
        self.game = game
        self.clock = pygame.time.Clock()
        self.game_view = game_view
        self.frame_rate = frame_rate
        self.initial_game_state = copy.deepcopy(game)
        self.auto_restart = auto_restart
        self.harvest = harvest

    @abc.abstractmethod
    def get_action(self) -> Direction | None:
        ...

    def game_loop(self) -> None:
        GameStats.track(self.game)
        with Live(GameStats.rich_table(), auto_refresh=False, screen=True) as live:
            while not self.game.game_over:  # single-game loop
                self.game.update(self.get_action())
                if self.game.score == self.harvest:
                    self.game.game_over = True
                self.game_view.update()
                live.update(GameStats.rich_table())
                live.refresh()
                self.clock.tick(self.frame_rate)

    def run(self) -> None:
        while True:  # outer "restart" loop
            self.game = copy.deepcopy(self.initial_game_state)
            if isinstance(self.game_view, GraphicsGameView):
                self.game_view.game = self.game
            self.game_loop()
            if self.auto_restart:
                continue
            # game over and no auto_restart, wait for user input to quit or restart
            if isinstance(self.game_view, GraphicsGameView):
                while True:
                    restart = self.handle_restart_key(self.handle_quit_key(pygame.event.get()))
                    if restart:
                        break
                    time.sleep(0.1)
            else:
                user_input = input("[R]estart or [Q]uit?")
                while user_input not in "rRQq":
                    user_input = input("[R]estart or [Q]uit?")
                if user_input in "Qq":
                    pygame.quit()
                    sys.exit()

    def handle_restart_key(self, events: list[pygame.event.Event]) -> bool:
        """While this handler is listening, press R to restart.

        Only relevant when graphics are being used. The implementation is somewhat naive and will
        eventually crash due to recursion limit (somewhere around 1,000 restarts).
        """
        return any(
            [event.type == pygame.KEYDOWN and event.key in {ord("R"), ord("r")} for event in events]
        )

    def handle_quit_key(self, events: list[pygame.event.Event]) -> list[pygame.event.Event]:
        """Only relevant when graphics are being used. Makes escape key cause game to quit.

        While escape key is not pressed, just passes through events.
        """
        if isinstance(self.game_view, GraphicsGameView):
            escape = any(
                [event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE for event in events]
            )
            if escape:
                pygame.quit()
                sys.exit()
        return events


class Keyboard(Controller):
    def get_action(self) -> Direction | None:
        direction = None
        for event in self.handle_quit_key(pygame.event.get()):
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
                direction = key_map.get(event.key)
        return direction


A = TypeVar("A", bound=BaseAgent)


class Agent(Controller):
    def __init__(
        self,
        agent_class: type[A] | str,
        agent_args: Iterable[Any] = (),
        agent_kwargs: Mapping[Any, Any] | None = None,
        game_view: GameView | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Same init logic as Controller base class, but...

        * provides a default headless game view
        * accepts arguments for initializing an AI agent:
            * agent_class: should be a class or python module path, e.g., "agents.SpinnerAgent"
            * agent_args: an iterable of positional arguments to pass to the agent
            * agent_args: an mapping of keyword arguments to pass to the agent
        * Agent class given by agent_class should implement a get_action(self, game) method
            that returns either a single action or list of actions. If the agent returns an empty
            list, it will be treated the same as [None]
        """
        super().__init__(game_view=game_view or HeadlessGameView(), *args, **kwargs)  # type: ignore
        if isinstance(agent_class, str):
            module_path, class_name = (
                ".".join((parts := agent_class.split("."))[:-1]),
                parts[-1],
            )
            AgentModule = importlib.import_module(module_path)
            AgentClass: type[A] = getattr(AgentModule, class_name)
        else:
            AgentClass = agent_class
        if agent_kwargs is None:
            agent_kwargs = {}
        self.agent_instance: A = AgentClass(*agent_args, **agent_kwargs)
        self.actions: list[Direction] = []

    def get_action(self) -> Direction | None:
        """Effectively acts as an adapter between Game, View, and Agent"""
        self.handle_quit_key(pygame.event.get())
        if not self.actions:
            new_actions: Iterable[Direction] | Direction | None = self.agent_instance.get_action(
                self.game
            )
            if isinstance(new_actions, Direction):
                # This agent decided to return 1 action instead of a whole list.
                # Wrap in a list so we can just treat both cases as the same.
                new_actions = [new_actions]
            elif not new_actions:
                return None
            # convert any other iterable type to list so we can pop()
            self.actions = list(new_actions)

        return self.actions.pop(0)
