"""Controller hooks for introspecting game state changes over time."""
import math
import sys
import time
from typing import Any, Callable

import pygame
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

import agents
import controllers
import stats
import views
from controllers import Controller


def get_agent_if_q(controller: Controller):
    """Returns the agent instance if the controller is running a QQ agent"""
    if (agent := getattr(controller, "agent_instance", None)) and isinstance(agent, agents.QQ):
        return agent


def register_new_game_with_stats(controller: Controller):
    stats.GameStats.new_game(controller.game)


def auto_restart_on_game_over(controller: Controller):
    if controller.auto_restart:
        raise controllers.Restart


def graphics_game_over(controller: Controller):
    if isinstance(controller.game_view, views.GraphicsGameView):
        while True:
            for event in pygame.event.get():
                keyboard_control(event)
            time.sleep(0.1)


def headless_game_over(controller: Controller):
    if isinstance(controller.game_view, views.HeadlessGameView):
        user_input = input("[R]estart or [Q]uit?")
        while user_input not in "rRQq":
            user_input = input("[R]estart or [Q]uit?")
        if user_input in "Rr":
            raise controllers.Restart
        # else let the controller quit


def update_game_stats(controller: Controller, *args: Any, **kwargs: Any):
    stats.GameStats.update_game(controller.game)


def update_live_display(controller: Controller, live: Live):
    game_table = stats.GameStats.live_display()
    game_layout = Layout(game_table, name="game table")
    ascii_layout = Layout(Panel(controller.game.to_ascii()), name="ascii panel")
    base_layout = Layout()
    base_layout.split_row(game_layout, ascii_layout)
    agent: agents.QQ
    if agent := get_agent_if_q(controller):
        column_headers = [
            "# total",
            "#[Q>0]",
            "#[Q=0]",
            "#[Q<0]",
            "#[Q=nan]",
            "#[Q=-inf]",
            "sum(Q)",
        ]
        q_summary_table = Table(*column_headers)
        vals = agent.Q.values()
        q_summary_table.add_row(
            *(
                str(e)
                for e in (
                    len(vals),
                    sum(1 for v in vals if v > 0),
                    sum(1 for v in vals if v == 0),
                    sum(1 for v in vals if v < 0),
                    sum(1 for v in vals if math.isnan(v)),
                    sum(1 for v in vals if v == float("-inf")),
                    sum(v for v in vals if v != float("-inf") and not math.isnan(v)),
                )
            )
        )
        q_agent_table = Table(
            "discount",
            "learning_rate",
            "learning_rate_decay",
            "exploration_rate",
            "exploration_rate_decay",
            "discount",
        )
        q_agent_table.add_row(
            str(agent.discount),
            str(agent.learning_rate),
            str(agent.learning_rate_decay),
            str(agent.exploration_rate),
            str(agent.exploration_rate_decay),
            str(agent.discount),
        )
        q_value_table = Table("<-🍎", "🍎->", "🍎^", "🍎v", "<-🐍", "🐍->", "🐍^", "🐍v", "act", "$")
        q_value_items = sorted(agent.Q.items(), key=lambda e: e[1])
        q_value_items_joined = [
            state + (action,) + (value,) for (state, action), value in q_value_items
        ]
        for row in q_value_items_joined:
            q_value_table.add_row(*[str(r) for r in row])

        base_layout["game table"].split(
            Layout(q_agent_table), Layout(q_summary_table), Layout(q_value_table, ratio=2)
        )
    live.update(base_layout)
    live.refresh()


def update_game_view(controller: Controller, live: Live):
    controller.game_view.update(controller.game)


def stop_for_harvest(controller: Controller, live: Live):
    if controller.harvest and controller.harvest == controller.game.score:
        raise controllers.Stop


def keyboard_control(key_event: pygame.event.Event):
    if not key_event.type == pygame.KEYDOWN:
        return

    match key_event.key:
        case pygame.K_ESCAPE | pygame.K_q:
            pygame.quit()
            sys.exit()
        case pygame.K_r:
            raise controllers.Restart
        case _:
            pass


on_new_game: list[Callable[[Controller], None]] = [register_new_game_with_stats]
on_game_over: list[Callable[[Controller], None]] = [
    auto_restart_on_game_over,
    graphics_game_over,
    headless_game_over,
    update_game_stats,
]
on_tick: list[Callable[[Controller, Live], None]] = [
    update_game_view,
    update_game_stats,
    update_live_display,
    stop_for_harvest,
]
on_pygame_event: list[Callable[[pygame.event.Event], None]] = [keyboard_control]

controllers.on_tick.extend(on_tick)
controllers.on_new_game.extend(on_new_game)
controllers.on_pygame_event.extend(on_pygame_event)
controllers.on_game_over.extend(on_game_over)
