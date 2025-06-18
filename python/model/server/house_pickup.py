from .dynamic_pickup import DynamicPickup as BaseDynamicPickup

class HousePickup(BaseDynamicPickup):

    def __init__(self, id: int):
        super().__init__(id)

    def set_house(self, house):
        self.house = house

    @classmethod
    def create(
            cls,
            model_id: int,
            type: int,
            x: float,
            y: float,
            z: float,
            world_id: int = -1,
            interior_id: int = -1,
            player_id: int = -1,
            stream_distance: float = 200.0,
            area_id: int = -1,
            priority: int = 0,
    ) -> "HousePickup":
        return super().create(model_id, type, x, y, z, world_id, interior_id, player_id, stream_distance, area_id, priority)
