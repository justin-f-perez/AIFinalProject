#!/usr/bin/env -S conda run --no-capture-output -n ai-final python3
"""See `--help`. Note that the ^shebang^above^ assumes you have created the
conda environment from the .yml file. If you don't have a conda environment
named ai-final, you can still run this file by executing it with the python
interpreter for which you installed the dependencies. For example:

    source venv/bin/activate
    python3 cli.py --help
"""
import argparse
import importlib
import logging
import random
import sys
from pathlib import Path

import pygame

import controllers
from agents import BaseAgent
from game import Game
from utils import Coordinate, get_timestamped_file_path
from views import GraphicsGameView, HeadlessGameView

DEBUG_LOG_DIR = Path(__file__).parent / "debug-logs"


def configure_logging(keep_previous: bool, log_level: int | None = None) -> None:
    """Sets up the logging used by all files in this project.

    If log_level is None, no logging is configured (at least by us).
    """
    if not keep_previous:
        for f in DEBUG_LOG_DIR.iterdir():
            f.unlink()
        DEBUG_LOG_DIR.rmdir()
        DEBUG_LOG_DIR.mkdir()

    if log_level:
        DEBUG_LOG_DIR.mkdir(exist_ok=True)
        debug_log_file_path = get_timestamped_file_path(dir=DEBUG_LOG_DIR, suffix=".log")
        logging.basicConfig(level=log_level, force=True, filename=debug_log_file_path)
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
        "--hooks",
        type=importlib.import_module,
        default="hooks",
        help="""
        One or more python module paths to be imported before the controller is initialized.
        The module may extend the lists of event listeners defined on the Controller class in the
        controllers module. The default hooks can be used as a reference.
        """,
        nargs="*",
    )
    argparser.add_argument(
        "--frame-rate",
        default=None,
        help="For manual mode. Determines frame rate (and difficulty).",
        type=int,
    )
    argparser.add_argument(
        "--screen-width",
        default=1200,
        help="How many pixels wide the game window should be.",
        type=int,
    )
    argparser.add_argument(
        "--screen-height",
        default=800,
        help="How many pixels tall the game window should be.",
        type=int,
    )

    game_parameter_parser = argparser.add_argument_group(
        "Game Parameters", "Control parameters that influence game state."
    )
    game_parameter_parser.add_argument(
        "--harvest",
        default=None,
        help="""
        Harvest big snakes- i.e., end the game once it reaches the given score.

        Useful in combination with --auto-restart to perform timed tests. Note that
        score is equal to the number of food eaten. This will not be equal to snake length
        because initial snake length is always greater than zero.
        """,
        type=int,
    )
    game_parameter_parser.add_argument(
        "--grid-width",
        default=12,
        help="The number of blocks wide the play space should be (default 72).",
        type=int,
    )
    game_parameter_parser.add_argument(
        "--grid-height",
        default=8,
        help="The number of blocks tall the play space should be (default 48).",
        type=int,
    )
    game_parameter_parser.add_argument(
        "--food", type=int, default=2, help="How many fruit to spawn at a time."
    )
    game_parameter_parser.add_argument(
        "--seed", type=str, help="Provide a seed for the random number generator."
    )

    log_levels = [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ]

    # argparser.add_mutually_exclusive_group(
    # "Note that currently mutually exclusive argument groups do not support
    # the title and description arguments of add_argument_group()."
    # https://docs.python.org/3/library/argparse.html (3.10)
    log_level_group = argparser.add_argument_group(
        "Logging",
        "Control the verbosity of the debug-logs" f"(Logs are written to {DEBUG_LOG_DIR})",
        # required=False,  # <--- add_mutually_exclusive_group
    )
    for level in log_levels:
        name = logging.getLevelName(level)
        log_level_group.add_argument(
            f"--{name.lower()}",
            action="store_const",
            dest="log_level",
            const=level,
            default=logging.WARNING,
            help=(
                f"Set the log level to {name}{' (default)' if level == logging.WARNING else ''}. "
            ),
        )
    log_level_group.add_argument(
        "--no-log",
        action="store_const",
        dest="log_level",
        const=None,
        default=logging.WARNING,
        help="Disable logging (no log file will be written)",
    )
    log_level_group.add_argument(
        "--keep-logs",
        action="store_true",
        help="Keep the debug-log directory from previous runs (default behavior is to delete.)",
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
    agent_choices = sorted(f"{s.__name__}" for s in BaseAgent.__subclasses__())
    # controller_group.add_argument("--agent", choices=agent_choices)

    subparsers = argparser.add_subparsers()
    agent_parser = subparsers.add_parser("agent")
    agent_parser.add_argument(
        "agent",
        choices=agent_choices,
        help="Choose an AI agent to play the game.",
    )
    agent_parser.add_argument(
        "--no-auto-restart",
        action="store_false",
        dest="auto_restart",
        help="Automatically restart after losing game.",
    )

    keyboard_parser = subparsers.add_parser("keyboard")
    keyboard_parser.add_argument(
        "keyboard",
        action="store_true",
    )

    args = argparser.parse_args()
    args.keyboard = hasattr(args, "keyboard")
    if not args.Graphics:
        args.Graphics = GraphicsGameView if getattr(args, "keyboard", None) else HeadlessGameView
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

    configure_logging(keep_previous=args.keep_logs, log_level=args.log_level)

    random.seed(args.seed if args.seed else "seed")
    game = Game(
        food=Coordinate.random(
            grid_width=args.grid_width, grid_height=args.grid_height, n=args.food
        ),
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
    common_controller_kwargs = {
        "game": game,
        "game_view": game_view,
        "frame_rate": args.frame_rate or (25 if args.keyboard else 0),
        "harvest": args.harvest,
    }
    if args.keyboard:
        controller = controllers.Keyboard(**common_controller_kwargs)
    else:
        assert args.agent
        controller = controllers.Agent(
            agent_class=args.agent, auto_restart=args.auto_restart, **common_controller_kwargs
        )
    controller.run()


if __name__ == "__main__":
    main()
