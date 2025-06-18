
from pystreamer.dynamictextlabel import DynamicTextLabel as BaseDynamicTextLabel
from samp import INVALID_PLAYER_ID, INVALID_VEHICLE_ID # type: ignore
from ..registrymixin import RegistryMixin

class Labale(BaseDynamicTextLabel, RegistryMixin[int, "Labale"]):
    def __init__(self, id: int):
        super().__init__(id)

    @classmethod
    def create(
        cls,
        text: str,
        color: int,
        x: float,
        y: float,
        z: float,
        draw_distance: float,
        attached_player: int = INVALID_PLAYER_ID,
        attached_vehicle: int = INVALID_VEHICLE_ID,
        testlos: bool = False,
        world_id: int = -1,
        interior_id: int = -1,
        player_id: int = -1,
        stream_distance: float = 200.0,
        area_id: int = -1,
        priority: int = 0,
    ) -> "Labale":
        return super().create(text, color, x, y, z, draw_distance, attached_player, attached_vehicle, True, world_id, interior_id, player_id, stream_distance, area_id, priority) # type: ignore
    
    def init_label(self, dbid: int, text: str, color: str, x: float, y: float, z: float, dd: float, vw: int, interior: int):
        self.dbid = dbid
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.z = z
        self.dd = dd
        self.vw = vw
        self.interior = interior

    def get_id(self) -> int:
        return super().id
