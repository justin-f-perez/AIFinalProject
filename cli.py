#!/usr/bin/env -S conda run --no-capture-output -n ai-final python3
"""
EXAMPLE USAGE:

./run --keyboard  # --graphics is implied
./run --agent agents.Spinner  # --headless is implied if --graphics is not given
./run --agent agents.GentleBrute --graphics --grid-height 10 --grid-width 10
./run --agent agents.TailChaser --graphics --frame-rate 0
"""
import argparse
import logging
import sys

import pygame

import controllers
from game import Game
from views import GraphicsGameView, HeadlessGameView


def configure_logging(log_level: int | None = None) -> None:
    """Sets up the logging used by all files in this project.

    If log_level is None (default), then the log level is set to WARNING.
    """
    if not log_level:
        log_level = logging.WARNING
    logging.basicConfig(level=log_level, force=True)
    logging.log(log_level, f"Log level configured to {log_level=}")


def initialize_pygame() -> None:
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
        default=25,
        help="The number of blocks wide the play space should be (default 72).",
        type=int,
    )
    argparser.add_argument(
        "--grid-height",
        default=25,
        help="The number of blocks tall the play space should be (default 48).",
        type=int,
    )
    argparser.add_argument(
        "--screen-width",
        default=1000,
        help="How many pixels wide the game window should be.",
        type=int,
    )
    argparser.add_argument(
        "--screen-height",
        default=1000,
        help="How many pixels tall the game window should be.",
        type=int,
    )
    argparser.add_argument("--food", type=int, default=2, help="How many fruit to spawn at a time.")

    log_levels = [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ]
    log_level_group = argparser.add_mutually_exclusive_group(required=False)
    for level in log_levels:
        name = logging.getLevelName(level)
        log_level_group.add_argument(
            f"--{name.lower()}",
            action="store_const",
            dest="log_level",
            const=level,
            help=f"Set the log level to {name}{' (default)' if level == logging.WARNING else ''}",
        )

    graphics_group = argparser.add_mutually_exclusive_group(required=False)
    graphics_group.add_argument(
        "--graphics",
        action="store_const",
        dest="Graphics",
        const=GraphicsGameView,
        help="Display game state in graphical mode (should be avoided for headless agents)",
    )
    graphics_group.add_argument(
        "--headless",
        action="store_const",
        dest="Graphics",
        const=HeadlessGameView,
        help="Display game state in graphical mode (should be avoided for headless agents)",
    )
    controller_group = argparser.add_mutually_exclusive_group(required=True)
    controller_group.add_argument(
        "--keyboard",
        action="store_true",
    )
    controller_group.add_argument(
        "--agent",
    )

    args = argparser.parse_args()
    if not args.Graphics:
        args.Graphics = GraphicsGameView if args.keyboard else HeadlessGameView
    return args


def main() -> None:
    """Basic housekeeping stuff

    * configure logging
    * initialize pygame
    * parse args
    * initialize game view
    * initialize game model
    """
    initialize_pygame()
    args = parse_args()

    configure_logging(log_level=args.log_level)
    game = Game(
        food_count=args.food,
        grid_width=args.grid_width,
        grid_height=args.grid_height,
    )
    game_view = args.Graphics(
        game=game,
        caption="snAIke",
        screen_width=args.screen_width,
        screen_height=args.screen_height,
        frame_rate=args.frame_rate,
    )
    controller: controllers.Controller
    if args.keyboard:
        controller = controllers.Keyboard(
            game=game, game_view=game_view, frame_rate=args.frame_rate
        )
    else:
        assert args.agent

        controller = controllers.Agent(
            agent_class=args.agent,
            game=game,
            game_view=game_view,
            frame_rate=args.frame_rate,
        )
    controller.run()


if __name__ == "__main__":
    main()
