from dataclasses import dataclass, field
from .model import Model
from pysamp.object import Object
from pystreamer.dynamicobject import DynamicObject
from .gate import Gate
from typing import ClassVar

@dataclass
class Map():
    _registry: ClassVar[dict[str, "Map"]] = {}

    name: str = ""
    description: str  = ""
    position: tuple[float, float, float, int, int] = (0.0, 0.0, 0.0, 0, 0) # (x, y, z, interior, virtualword)
    models: list[Model] = field(default_factory=list)
    created: str  = ""
    author: str  = ""
    is_active: bool  = True
    static_objects: list[Object] = field(default_factory=list)
    dynamic_objects: list[DynamicObject] = field(default_factory=list)
    remove_objects: list[tuple] = field(default_factory=list)
    gates: list [Gate] = field(default_factory=list)

    #region registry
    @classmethod 
    def add_registry_item(cls, name: str, obj: "Map") -> None:
        cls._registry[name] = obj

    @classmethod
    def get_registry_items(cls) -> list["Map"]:
        return list(cls._registry.values())
    
    @classmethod
    def get_registry_items_with_keys(cls):
        return sorted(cls._registry.items())

    @classmethod
    def get_registry_item(cls, name: str) -> "Map":
        return cls._registry.get(name, None)
    
    @classmethod
    def remove_from_registry(cls, map: "Map"):
        del cls._registry[map.name]
    #endregion registry
