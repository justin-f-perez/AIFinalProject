import abc
import logging
import random
from typing import Any

import pygame

from game import Game
from utils import Color


class GameView(abc.ABC):
    @abc.abstractmethod
    def update(self) -> None:
        ...


class GraphicsGameView(GameView):
    def __init__(
        self,
        game: Game,
        caption: str,
        screen_width: int,
        screen_height: int,
        frame_rate: int,
    ):
        super().__init__()
        self.game = game
        self.game_over_font = pygame.font.SysFont("times", 20)
        self.default_font = pygame.font.SysFont("consolas", 20)
        self.frame_rate = frame_rate
        self.game_window: pygame.surface.Surface = pygame.display.set_mode(
            (screen_width, screen_height),
        )
        self.segment_width = screen_width / self.game.grid_width
        self.segment_height = screen_height / self.game.grid_height
        logging.debug("GraphicsGameView initialized")

    def update(self) -> None:
        self.draw()
        pygame.display.update()

    def draw(self) -> None:
        self.game_window.fill(Color.BLACK.value)
        for segment in self.game.snake._segments:
            pygame.draw.rect(
                self.game_window,
                Color.GREEN.value,
                pygame.Rect(
                    segment.X * self.segment_width,
                    segment.Y * self.segment_height,
                    self.segment_width,
                    self.segment_height,
                ),
            )

        # Snake food
        for food_pos in self.game.food:
            pygame.draw.rect(
                self.game_window,
                Color.WHITE.value,
                pygame.Rect(
                    food_pos.X * self.segment_width,
                    food_pos.Y * self.segment_height,
                    self.segment_width,
                    self.segment_height,
                ),
            )

        if self.game.game_over:
            you_died_font = pygame.font.SysFont("times new roman", 90)
            you_died_phrases = (
                "You died.",
                "YOU ARE DEAD",
                "Wasted",
                "Insert (25c)",
                "Game over",
                "Tilt!",
                "MUERTO",
                "404 Not Found",
            )
            game_over_surface = you_died_font.render(
                random.choice(you_died_phrases), True, Color.RED.value
            )
            game_over_rect = game_over_surface.get_rect()
            game_over_rect.midtop = (
                self.game_window.get_width() // 2,
                self.game_window.get_height() // 4,
            )
            self.game_window.blit(game_over_surface, game_over_rect)
            self.show_score()
            pygame.display.flip()

        else:
            self.show_score()

    def show_score(self) -> None:
        score_font = pygame.font.SysFont("times" if self.game.game_over else "consolas", 20)
        score_surface = score_font.render(
            f"Score: {self.game.score}",
            True,
            Color.RED.value if self.game.game_over else Color.WHITE.value,
        )
        score_rect = score_surface.get_rect()
        score_rect.midtop = (
            (
                self.game_window.get_width() // 2,
                int(self.game_window.get_height() // 1.25),
            )
            if self.game.game_over
            else (self.game_window.get_width() // 10, 15)
        )
        self.game_window.blit(score_surface, score_rect)


class HeadlessGameView(GameView):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logging.debug("HeadlessGameView initialized")

    def update(self) -> None:
        pass
