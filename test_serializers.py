from serializers import _to_dict, _to_json, _to_yaml


def test_to_json(game):
    assert (
        _to_json(game)
        == '{"food": [{"X": 3, "Y": 3}, {"X": 2, "Y": 2}], "grid_height": 5, "grid_width": 5, "score": 0, "snake": {"segments": [{"X": 1, "Y": 2}, {"X": 1, "Y": 1}, {"X": 2, "Y": 1}]}, "ticks": 0}'  # noqa: E501
    )


def test_mixin_to_json(game):
    assert game.to_json() == _to_json(game)


def test_to_yaml(game):
    assert (
        _to_yaml(game)
        == "food:\n- X: 3\n  Y: 3\n- X: 2\n  Y: 2\ngrid_height: 5\ngrid_width: 5\nscore: 0\nsnake:\n  segments:\n  - X: 1\n    Y: 2\n  - X: 1\n    Y: 1\n  - X: 2\n    Y: 1\nticks: 0\n"  # noqa: E501
    )


def test_mixin_to_yaml(game):
    assert game.to_yaml() == _to_yaml(game)


def test_to_dict(game):
    assert _to_dict(game) == {
        "grid_width": 5,
        "grid_height": 5,
        "snake": {"segments": [{"X": 1, "Y": 2}, {"X": 1, "Y": 1}, {"X": 2, "Y": 1}]},
        "food": [{"X": 3, "Y": 3}, {"X": 2, "Y": 2}],
        "score": 0,
        "ticks": 0,
    }


def test_mixin_to_dict(game):
    assert game.to_dict() == _to_dict(game)
