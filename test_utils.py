import random

from game import Game
from utils import Direction, PriorityQueue


def test_priority_queue(game: Game) -> None:
    """Test items with lowest priority are popped first."""
    order = [(game, Direction.random())]
    for successor in game.successors:
        order.append((successor, Direction.random()))

    pq = PriorityQueue()
    for _ in range(25):  # 25 rounds of random shuffling
        assert pq.empty
        state_priority_pairs = [(successor, i * 10) for i, successor in enumerate(order)]
        random.shuffle(state_priority_pairs)
        for item, priority in state_priority_pairs:
            pq.push(item=item, priority=priority)
            assert item in pq
        assert pq.has_items

        for item in order:
            assert pq.pop() == item
    assert pq.empty
