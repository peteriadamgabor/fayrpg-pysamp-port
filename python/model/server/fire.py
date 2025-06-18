import threading
from itertools import count
from dataclasses import dataclass, field

from pystreamer.dynamicobject import DynamicObject



@dataclass
class Flame:
    flame_object: DynamicObject
    fier: "Fier"
    health: float = 100.0

@dataclass
class Fier:
    center: tuple[float, float, float]
    flames: list[Flame] = field(default_factory=list)
    id: int = field(default_factory=count().__next__)
