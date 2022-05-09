import abc
import copy
import importlib
import logging
import sys
from dataclasses import dataclass, replace
from typing import Any, Callable, Iterable, Mapping, TypeVar

import pygame
from rich.live import Live

import agents
from agents import BaseAgent
from game import Game
from utils import Direction
from views import GameView, GraphicsGameView, HeadlessGameView

# NOTE: Not in the dataclass or abstract base because we want these to be globally defined.
#       This allows imported hook modules to wire themselves up to a known target.

on_tick: list[Callable[["Controller", Live], None]] = []
on_new_game: list[Callable[["Controller"], None]] = []
on_game_over: list[Callable[["Controller"], None]] = []
on_pygame_event: list[Callable[[pygame.event.Event], None]] = []


class Stop(Exception):
    """Signals a controller to stop the game."""

    pass


class Restart(Exception):
    """Signals a controller to restart the game."""

    pass


@dataclass
class _ControllerMixin:
    game: Game
    game_view: GameView
    frame_rate: int = 0
    auto_restart: bool = False
    harvest: int | None = None

    def __post_init__(self) -> None:
        self.initial_game_state = copy.deepcopy(self.game)
        self.clock = pygame.time.Clock()


class LiveDisplayMixin:
    live = Live()


class Controller(abc.ABC, _ControllerMixin):
    @abc.abstractmethod
    def get_action(self, events: list[pygame.event.Event]) -> Direction | None:
        ...

    def game_loop(self) -> None:
        for new_game_hook in on_new_game:
            new_game_hook(self)
        with Live(auto_refresh=False, screen=True) as live:
            while not self.game.game_over:
                events = pygame.event.get()
                for event_hook in on_pygame_event:
                    for event in events:
                        event_hook(event)
                self.game = self.game.update(self.get_action(events=events))
                for listener in on_tick:
                    try:
                        listener(self, live)
                    except (Stop, Restart):
                        raise
                    except Exception as ex:
                        raise Exception(f"A hook caused an unexpected error: {ex}")

                self.clock.tick(self.frame_rate)

    def game_over(self):
        for game_over_hook in on_game_over:
            game_over_hook(self)

    def run(self) -> None:
        while True:  # outer "restart" loop
            self.game = replace(self.initial_game_state)
            if isinstance(self.game_view, GraphicsGameView):
                self.game_view.game = self.game
            try:
                self.game_loop()
            except Stop:
                pass
            except Restart:
                continue

            try:
                self.game_over()
            except Restart:
                continue
            else:
                pygame.quit()
                sys.exit()


class Keyboard(Controller):
    def get_action(self, events: list[pygame.event.Event]) -> Direction | None:
        direction = None
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            match event.key:
                # fmt: off
                case pygame.K_UP | pygame.K_w: direction = Direction.UP
                case pygame.K_LEFT | pygame.K_a: direction = Direction.LEFT
                case pygame.K_DOWN | pygame.K_s: direction = Direction.DOWN
                case pygame.K_RIGHT | pygame.K_d: direction = Direction.RIGHT
                case _: pass
                # fmt: on

                # W=Up; S=Down; A=Left; D=Right
                # key_map = {
                #     pygame.K_UP: Direction.UP,
                #     ord("w"): Direction.UP,
                #     pygame.K_LEFT: Direction.LEFT,
                #     ord("a"): Direction.LEFT,
                #     pygame.K_DOWN: Direction.DOWN,
                #     ord("s"): Direction.DOWN,
                #     pygame.K_RIGHT: Direction.RIGHT,
                #     ord("d"): Direction.RIGHT,
                # }
                # direction = key_map.get(event.key)
        return direction if direction in self.game.snake.valid_actions else None


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
            if "." in agent_class:
                module_path, agent_class = agent_class.rsplit(".")
                agent_module = importlib.import_module(module_path)
            else:
                agent_module = agents
            AgentClass = getattr(agent_module, agent_class)
        else:
            AgentClass = agent_class
        agent_kwargs = agent_kwargs or {}
        self.agent_instance: A = AgentClass(*agent_args, **agent_kwargs)
        self.actions: list[Direction | None] = []
        self.action_history: list[Direction | None] = []

    def get_action(self, events: list[pygame.event.Event]) -> Direction | None:
        """Effectively acts as an adapter between Game, View, and Agent"""
        if len(self.actions) == 0:
            new_actions: Iterable[Direction] | Direction | None = self.agent_instance.get_action(
                self.game
            )
            # If this agent decided to return a single action rather than a
            # list, we wrap it in a list anyway so we can treat both cases the same
            match new_actions:
                case Direction():
                    self.actions = [new_actions]
                case None | [None] | (None,) | ():
                    direction = self.game.snake.direction
                    logging.info(f"Agent didn't provide an input. Continuing in {direction}")
                    self.actions = [direction]
                case [Direction(), *_] | (Direction(), *_):
                    self.actions = list(new_actions)
                case _:
                    raise Exception(f"Agent didn't return a valid value! {new_actions=}")

        next_action = self.actions.pop(0)
        self.action_history.append(next_action)
        return next_action
