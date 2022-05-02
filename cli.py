#!/usr/bin/env python3.10
import argparse
import logging
import sys

import pygame

import controllers
from game import Game
from snake import Snake
from utils import Coordinate, Direction
from view import GraphicsGameView, HeadlessGameView


def configure_logging():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


def initialize_pygame():
    _, num_errors = pygame.init()
    if num_errors > 0:
        logging.error(f"ABORT! {num_errors=} during init(), exiting...")
        sys.exit(-1)
    else:
        logging.info("initialized")


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--frame-rate",
        default=25,
        help="For manual mode. Determines frame rate (and difficulty).",
        type=int,
    )
    argparser.add_argument(
        "--grid-width",
        default=72,
        help="The number of blocks wide the play space should be (default 72).",
        type=int,
    )
    argparser.add_argument(
        "--grid-height",
        default=48,
        help="The number of blocks tall the play space should be (default 48).",
        type=int,
    )
    argparser.add_argument(
        "--screen-width",
        default=720,
        help="How many pixels wide the game window should be.",
        type=int,
    )
    argparser.add_argument(
        "--screen-height",
        default=480,
        help="How many pixels tall the game window should be.",
        type=int,
    )
    argparser.add_argument(
        "--food", type=int, default=2, help="How many fruit to spawn at a time."
    )

    graphics_group = argparser.add_mutually_exclusive_group(required=True)
    graphics_group.add_argument(
        "--graphics",
        action="store_true",
        dest="graphics",
        help="Display game state in graphical mode (should be avoided for headless agents)",
    )
    graphics_group.add_argument(
        "--headless",
        action="store_false",
        dest="graphics",
        help="Display game state in graphical mode (should be avoided for headless agents)",
    )
    controller_group = argparser.add_mutually_exclusive_group(required=True)
    controller_group.add_argument(
        "--keyboard",
        action="store_const",
        dest="Controller",
        const=controllers.Keyboard,
    )
    controller_group.add_argument(
        "--agent", action="store_const", dest="Controller", const=controllers.Agent
    )

    return argparser.parse_args()


def main():
    """Basic housekeeping stuff

    * configure logging
    * initialize pygame
    * parse args
    * initialize game view
    * initialize game model
    """
    configure_logging()
    initialize_pygame()
    args = parse_args()

    snake = Snake(
        segments=[Coordinate(1, 1), Coordinate(1, 0), Coordinate(0, 0)],
        direction=Direction.DOWN,
    )
    game = Game(
        food_count=args.food,
        grid_width=args.grid_width,
        grid_height=args.grid_height,
        snake=snake,
    )

    if args.graphics:
        game_view = GraphicsGameView(
            game=game,
            caption="snAIke",
            screen_width=args.screen_width,
            screen_height=args.screen_height,
            frame_rate=args.frame_rate,
        )
    else:
        game_view = HeadlessGameView(game)

    controller = args.Controller(
        game=game, game_view=game_view, frame_rate=args.frame_rate
    )
    controller.run()


if __name__ == "__main__":
    main()
