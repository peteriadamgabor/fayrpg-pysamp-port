from .interior import Interior
from .zone import DynamicZone

class InteriortDynamicZone(DynamicZone):
    def __init__(self, id: int):
        super().__init__(id)
        self.interior: Interior | None
