import copy

from game import Game
from snake import Snake


def test_successors(game: Game) -> None:
    successors = game.successors
    for successor in successors:
        assert successor.snake.head != game.snake.head


def test_equality(game: Game) -> None:
    game_copy = copy.deepcopy(game)
    # show these are not the same
    assert id(game_copy) != id(game)
    assert id(game_copy.snake) != id(game.snake)
    assert id(game_copy.food) != id(game.food)
    assert game_copy == game
    assert game_copy in [game]
    assert game_copy in (game,)

    game_copy.food = {*game.food}
    assert game_copy == game
    game_copy.snake = Snake(game.snake._segments, game.snake._direction)
    assert game_copy == game
