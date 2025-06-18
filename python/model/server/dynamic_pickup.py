from pystreamer.dynamicpickup import DynamicPickup as BaseDynamicPickup

class DynamicPickup(BaseDynamicPickup):
    _registry: dict[int, "BaseDynamicPickup"] = {}


    def __init__(self, id: int):
        super().__init__(id)

    @classmethod
    def add_registry_item(cls, id: int, obj: "BaseDynamicPickup") -> None:
        cls._registry[id] = obj


    @classmethod
    def get_registry_items(cls) -> list["BaseDynamicPickup"]:
        return list(cls._registry.values())
    
    @classmethod
    def get_registry_items_with_keys(cls):
        return cls._registry.items()


    @classmethod
    def get_registry_item(cls, id: int) -> "BaseDynamicPickup":
        return cls._registry.get(id, None)
    

    @classmethod
    def remove_from_registry(cls, zone: "BaseDynamicPickup"):
        del cls._registry[zone.id]


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
    ) -> "DynamicPickup":
        return super().create(model_id, type, x, y, z, world_id, interior_id, player_id, stream_distance, area_id, priority)

