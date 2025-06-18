import json
from dataclasses import dataclass
from typing import Any

from .material_text import MaterialText
from .material import Material


@dataclass
class Object:
    name: str
    model_id: int
    x: float
    y: float
    z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float
    world_id: int
    interior_id: int
    stream_distance: float
    draw_distance: float
    static: bool
    materials: list["Material"]
    material_texts: list["MaterialText"]

    @staticmethod
    def from_dict(obj: Any) -> 'Object':
        _name = str(obj.get("name"))
        _model_id = int(obj.get("model_id"))
        _x = float(obj.get("x"))
        _y = float(obj.get("y"))
        _z = float(obj.get("z"))
        _rotation_x = int(obj.get("rotation_x"))
        _rotation_y = int(obj.get("rotation_y"))
        _rotation_z = int(obj.get("rotation_z"))
        _world_id = int(obj.get("world_id"))
        _interior_id = int(obj.get("interior_id"))
        _stream_distance = float(obj.get("stream_distance"))
        _draw_distance = float(obj.get("draw_distance"))
        _static = bool(obj.get("static"))
        _materials = [Material.from_dict(y) for y in obj.get("materials")]
        return Object(_name, _model_id, _x, _y, _z, _rotation_x, _rotation_y, _rotation_z, _world_id, _interior_id,
                      _stream_distance, _draw_distance, _static, _materials)

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)
