from pysamp import call_native_function
from pysamp.pickup import Pickup as BasePickup


class Pickup(BasePickup):

    def __init__(self, id: int):
        super().__init__(id)

    def set_model(self, model_id):
        return call_native_function("SetPickupModel", self.id, model_id, True)

    @classmethod
    def create(
            cls,
            model: int,
            type: int,
            x: float,
            y: float,
            z: float,
            virtual_world: int = 0,
    ) -> "Pickup":
        return super().create(model, type, x, y, z, virtual_world)
