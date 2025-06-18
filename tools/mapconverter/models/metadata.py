import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .material_text import MaterialText
from .material import Material


@dataclass
class Metadata:
    name: str
    description: str
    author: str
    created: str
    position: list[float | int]
    models: list[str]
    is_active: bool = True

    @staticmethod
    def from_dict(obj: Any) -> 'Metadata':
        _name = str(obj.get("name"))
        _description = str(obj.get("description"))
        _author = str(obj.get("author"))
        _created = str(obj.get("created"))
        _position = [y for y in obj.get("position")]
        _models = [y for y in obj.get("models")]
        _is_active = bool(obj.get("is_active"))

        return Metadata(_name, _description, _author, _created, _position, _models, _is_active)

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)
