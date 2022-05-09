from snake import Snake
from utils import Coordinate, Direction


def test_valid_actions() -> None:
    head = Coordinate(1, 0)
    tail = Coordinate(0, 0)
    snake = Snake(segments=(head, tail))
    assert snake.direction == Direction.RIGHT
    assert {Direction.UP, Direction.RIGHT, Direction.DOWN} == snake.valid_actions


def test_ouroboros() -> None:
    """
    In a clock-wise loop where the first and final nodes are the same, ouroboros should be True
    when the snake's head is not touching any other body part, it should be False.
    """
    no_collision = (
        Coordinate(0, 0),
        Coordinate(1, 0),
        Coordinate(1, 1),
        Coordinate(0, 1),
    )
    collision = no_collision + (Coordinate(0, 0),)

    assert Snake(segments=collision).ouroboros
    assert not Snake(segments=no_collision).ouroboros


def test_direction() -> None:
    segments = (Coordinate(0, 1), Coordinate(0, 0))
    # first segment is head, and the Y coordinate is one greater than the following coordinate.
    # in computer graphics, incrementing Y corresponds to moving farther down on the screen
    assert Snake(segments=segments).direction == Direction.DOWN


def test_bodily_integrity() -> None:
    head = Coordinate(0, 0)
    neck = Coordinate(0, 1)
    extra = Coordinate(0, 2)
    tail = Coordinate(0, 3)
    snake = Snake(segments=(head, neck, extra, tail))
    assert snake.head == head
    assert snake.neck == neck
    assert snake.tail == tail


def test_move() -> None:
    head = Coordinate(1, 2)
    tail = Coordinate(1, 1)
    old_snake = Snake(segments=(head, tail))
    assert old_snake.direction == Direction.DOWN

    for direction in old_snake.valid_actions:
        new_snake = old_snake.move(direction=direction, grow=False)
        assert new_snake.tail == old_snake.head
        match direction:
            case Direction.LEFT:
                assert new_snake.head == Coordinate(old_snake.head.X - 1, head.Y)
            case Direction.RIGHT:
                assert new_snake.head == Coordinate(old_snake.head.X + 1, head.Y)
            case Direction.DOWN:
                assert new_snake.head == Coordinate(old_snake.head.X, head.Y + 1)

        new_snake = old_snake.move(direction=direction, grow=True)
        assert new_snake.tail == old_snake.tail
