from .zone import DynamicZone

class TeleportDynamicZone(DynamicZone):
    def __init__(self, id: int):
        super().__init__(id)
        self.__entrance: "Entrance" | None # type: ignore

    @property
    def entrance(self) -> "Entrance": # type: ignore
        if self.__entrance is None:
            raise Exception("teleport is not inited!")
        
        return self.__entrance

    @entrance.setter 
    def entrance(self, entrance: "Entrance") -> None: # type: ignore
        self.__entrance = entrance
