from dataclasses import replace

from game import Game
from snake import Snake


def test_successors(game: Game) -> None:
    successors = game.successors
    for successor in successors:
        assert successor != game
        assert successor.snake != game.snake
        assert successor.snake.head != game.snake.head
        for sucception in successor.successors:
            assert successor != game and successor != sucception and game != sucception
            assert (
                successor.snake != game.snake
                and successor.snake != sucception.snake
                and sucception.snake != game.snake
            )
            assert (
                successor.snake.head != game.snake.head
                and successor.snake.head != sucception.snake.head
                and game.snake.head != sucception.snake.head
            )


def test_equality(game: Game) -> None:
    # replace() doesn't really do anything if no values change
    game_copy = replace(game)
    assert id(game_copy) == id(game_copy)

    # but we can get a new object by changing the value to the existing one
    game_copy = replace(game, ticks=game.ticks)
    assert id(game_copy) == id(game_copy)

    # ticks should be ignored for equality & hashing
    game_copy = replace(game_copy, ticks=game.ticks + 1)
    assert game == game_copy
    assert game.snake == game_copy.snake
    assert game.food == game_copy.food
    assert id(game_copy) != id(game)
    assert hash(game_copy) == hash(game)

    # since ticks don't matter for equality and hashing, the 'in' operator
    # should treat the copy as the same key
    assert game_copy in [game]
    assert game_copy in (game,)
    assert game_copy in {game}

    game_copy = replace(game_copy, food=game.food)
    assert game_copy == game
    game_copy = replace(game_copy, snake=Snake(segments=game.snake.segments))
    assert game_copy == game
