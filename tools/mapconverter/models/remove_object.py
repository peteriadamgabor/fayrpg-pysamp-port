import json
from dataclasses import dataclass
from typing import Any

from .material_text import MaterialText
from .material import Material


@dataclass
class RemoveObject:
    model_id: int
    x: float
    y: float
    z: float
    radius: float

    @staticmethod
    def from_dict(obj: Any) -> 'RemoveObject':
        _model_id = int(obj.get("model_id"))
        _x = float(obj.get("x"))
        _y = float(obj.get("y"))
        _z = float(obj.get("z"))
        _r = float(obj.get("r"))
        return RemoveObject(_model_id, _x, _y, _z, _r)

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)
