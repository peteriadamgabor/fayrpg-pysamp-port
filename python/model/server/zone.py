from pystreamer.dynamiczone import DynamicZone as BaseDynamicZone
from python.utils.enums.zone_type import ZoneType

class DynamicZone(BaseDynamicZone):
    _registry: dict[int, "BaseDynamicZone"] = {}


    def __init__(self, id: int):
        super().__init__(id)
        self.x: float
        self.y: float
        self.z: float
        self.size: float

    @classmethod
    def add_registry_item(cls, id: int, obj: "BaseDynamicZone") -> None:
        cls._registry[id] = obj

    @classmethod
    def get_registry_items(cls) -> list["BaseDynamicZone"]:
        return list(cls._registry.values())
    
    @classmethod
    def get_registry_items_with_keys(cls):
        return cls._registry.items()

    @classmethod
    def get_registry_item(cls, id: int) -> "BaseDynamicZone":
        return cls._registry.get(id, None)
    
    @classmethod
    def remove_from_registry(cls, zone: "BaseDynamicZone"):
        del cls._registry[zone.id]

    @classmethod
    def create_sphere(
            cls,
            x: float,
            y: float,
            z: float,
            size: float,
            world_id: int = -1,
            interior_id: int = -1,
            player_id: int = -1,
            priority: int = 0,
    ) -> "DynamicZone":
        cls.x = x
        cls.y = y
        cls.z = z
        cls.size = size

        return super().create_sphere(float(x),
                                     float(y),
                                     float(z),
                                     float(size),
                                     world_id,
                                     interior_id,
                                     player_id,
                                     priority)

    @classmethod
    def create_circle(
            cls,
            x: float,
            y: float,
            size: float,
            world_id: int = -1,
            interior_id: int = -1,
            player_id: int = -1,
            priority: int = 0,
    ) -> "DynamicZone":
        cls.x = x
        cls.y = y
        cls.size = size

        return super().create_circle(
            float(x),
            float(y),
            float(size),
            int(world_id),
            int(interior_id),
            int(player_id),
            int(priority)
        )

    @classmethod
    def create_rectangle(
            cls,
            min_x: float,
            min_y: float,
            max_x: float,
            max_y: float,
            world_id: int = -1,
            interior_id: int = -1,
            player_id: int = -1,
            priority: int = 0,
    ) -> "DynamicZone":
        return super().create_rectangle(float(min_x),
                                        float(min_y),
                                        float(max_x),
                                        float(max_y),
                                        world_id,
                                        interior_id,
                                        player_id,
                                        priority)

    @classmethod
    def create_cuboid(
            cls,
            min_x: float,
            min_y: float,
            min_z: float,
            max_x: float,
            max_y: float,
            max_z: float,
            world_id: int = -1,
            interior_id: int = -1,
            player_id: int = -1,
            priority: int = 0,
    ) -> "DynamicZone":
        return super().create_cuboid(float(min_x),
                                     float(min_y),
                                     float(min_z),
                                     float(max_x),
                                     float(max_y),
                                     float(max_z),
                                     world_id,
                                     interior_id,
                                     player_id,
                                     priority)
