import abc
import sys

import pygame

from game import Game
from utils import Direction
from view import GameView


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
    next_direction = {
        Direction.UP: Direction.RIGHT,
        Direction.RIGHT: Direction.DOWN,
        Direction.DOWN: Direction.LEFT,
        Direction.LEFT: Direction.UP,
    }

    def get_action(self):
        # for some reason game window doesn't render if we don't consume the event queue
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # ESC = Quit
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        return self.next_direction[self.game.snake.direction]
