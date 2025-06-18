from dataclasses import dataclass
from typing import Any


@dataclass
class Material:
    material_index: int
    model_id: int
    txd_name: str
    texture_name: str
    material_color: int

    @staticmethod
    def from_dict(obj: Any) -> "Material":
        _material_index = int(obj.get("material_index"))
        _model_id = int(obj.get("model_id"))
        _txd_name = str(obj.get("txd_name"))
        _texture_name = str(obj.get("texture_name"))
        _material_color = int(obj.get("material_color"))
        return Material(_material_index, _model_id, _txd_name, _texture_name, _material_color)
