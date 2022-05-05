import pytest

from agents import (
    a_star,
    feeder_goal,
    min_man_heuristic,
    reciprocal_average_food_heuristic,
    tail_chaser_goal,
)
from game import Game
from snake import Snake
from utils import Coordinate, Direction, manhattan_distance, reciprocal

ORIGIN = Coordinate(0, 0)


@pytest.mark.parametrize(
    "coord",
    map(
        lambda pair: Coordinate(*pair),
        [(0, 0), (0, 1), (1, 0), (1, 1), (50, 0), (0, 50), (10, 10), (25, 50)],
    ),
)
def test_manhattan_distance(coord: tuple[int, int]) -> None:
    """test test_manhattan_distance calculates correct value

    test strategy:
    * given a list of test coordinates, we use origin (0,0) as the second coord
    * we only care about the positive integers (if a snake goes to negative coords, it dies)

    * this allows us to trivially calculate the expected value as:
        coord[0] + coord[1]
    * we test both orders for the args to manhattan_distance()
    """
    assert manhattan_distance(coord, ORIGIN) == coord[0] + coord[1]
    assert manhattan_distance(ORIGIN, coord) == coord[0] + coord[1]


@pytest.mark.parametrize(
    "head,food,expected",
    [
        (Coordinate(0, 0), {Coordinate(0, 1)}, reciprocal(0 + 1) / 1),  # =1
        (
            Coordinate(0, 0),
            {Coordinate(1, 0), Coordinate(0, 1)},
            reciprocal(((1 + 0) + (0 + 1)) / 2),
        ),  # =1
        (
            Coordinate(0, 0),
            {Coordinate(0, 6), Coordinate(6, 6), Coordinate(6, 0)},
            reciprocal(((0 + 6) + (6 + 6) + (6 + 0)) / 3),
        ),  # =8
    ],
)
def test_average_food_heuristic(
    game: Game, head: Coordinate, food: set[Coordinate], expected: float
) -> None:
    """test average_food_heuristic calculates correct value

    test strategy:
    * we only need snake head and food list, not whole game state
    * we just test against some pre-computed values:
    1.  head: (0,0), food: [(0,1)], expect: 1/1=1
    2.  head: (0,0), food: [(1,0),(0,1)], expect: 1+1/2=1
    3.  head: (0,0), food: [(0,6),(6,6),(6,0)], expect: (6)+(6+6)+(6)/3 =24/3 =8

    * given a list of test coordinates, we use origin (0,0) as the second coord
    * we only care about the positive integers (if a snake goes to negative coords, it dies)

    * this allows us to trivially calculate the expected value as:
        coord[0] + coord[1]
    * we test both orders for the args to manhattan_distance()
    """
    snake = Snake([head], Direction.UP)  # direction is arbitrary
    game.snake = snake
    game.food = food
    assert reciprocal_average_food_heuristic(game) == expected


@pytest.mark.timeout(30)
@pytest.mark.parametrize(
    "food_coords, expected_actions",
    [
        ({Coordinate(0, 0)}, ()),  # start state=goal state
        ({Coordinate(1, 0)}, (Direction.RIGHT,)),  # test directional movement
        ({Coordinate(0, 1)}, (Direction.DOWN,)),
        (  # test more than 1 move
            {Coordinate(2, 0)},
            (Direction.RIGHT, Direction.RIGHT),
        ),
        ({Coordinate(0, 2)}, (Direction.DOWN, Direction.DOWN)),
        ({Coordinate(50, 0)}, (Direction.RIGHT,) * 50),  # test a long one
        (  # test more than 1 food
            {Coordinate(2, 0), Coordinate(1, 0)},
            (Direction.RIGHT,),
        ),
        (  # test find nearest food
            {Coordinate(25, 0), Coordinate(0, 50)},
            (Direction.RIGHT,) * 25,
        ),
        (  # even more food
            [(25, 0)] + [(0, y) for y in range(30, 50)],
            (Direction.RIGHT,) * 25,
        ),
    ],
)
def test_a_star(
    food_coords: set[Coordinate], expected_actions: tuple[Direction], game: Game
) -> None:
    snake = Snake([Coordinate(0, 0), Coordinate(-1, 0)], Direction.DOWN)
    game.snake = snake
    game.food = {Coordinate(*food_coord) for food_coord in food_coords}
    assert (
        a_star(
            game,
            heuristic=min_man_heuristic,
            goal=lambda state: feeder_goal(state) and tail_chaser_goal(state),
        )
        == expected_actions
    )
