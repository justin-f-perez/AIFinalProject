import json
from typing import Any

import yaml


class SerializerMixin:
    def to_dict(self):
        return _to_dict(self)

    def to_yaml(self):
        return _to_yaml(self)

    def to_yml(self):
        return _to_yaml(self)

    def to_json(self):
        return _to_json(self)


def _serialize(obj: Any):
    if hasattr(obj, "_asdict"):
        return {k: _serialize(v) for k, v in obj._asdict().items()}
    if hasattr(obj, "__slots__") and hasattr(obj, "__getstate__"):
        return {k: _serialize(v) for k, v in zip(obj.__slots__, obj.__getstate__())}
    elif hasattr(obj, "__dict__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items()}
    else:
        match obj:
            case dict():
                return dict(sorted((k, _serialize(v)) for k, v in obj.items()))
            case (list() | set() | frozenset() | tuple()):
                return [_serialize(v) for v in obj]
            case (str() | int() | float()):
                return obj


def _to_dict(obj: Any):
    return _serialize(obj)


def _to_json(obj: Any):
    return json.dumps(_serialize(obj), sort_keys=True)


def _to_yaml(obj: Any):
    return yaml.dump(_serialize(obj), sort_keys=True)
