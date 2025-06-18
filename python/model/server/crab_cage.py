from dataclasses import dataclass
import datetime
from typing import Optional

from pystreamer.dynamicmapicon import DynamicMapIcon
from pystreamer.dynamicobject import DynamicObject

@dataclass
class CrabCage:
        id: int
        in_water: bool = False
        pos_x: float = 0.0
        pos_y: float = 0.0
        pos_z: float = 0.0
        time: datetime.datetime = datetime.datetime.now()
        bait: int = -1
        crabs: int = -1
        timer: int = -1
        object: Optional[DynamicObject] = None
        mapicon: Optional[DynamicMapIcon] = None