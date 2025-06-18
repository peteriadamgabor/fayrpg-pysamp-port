import itertools
from typing import override

from python.model.server import Player
from python.model.registrymixin import RegistryMixin
from python.model.server.teleport_dynamic_zone import TeleportDynamicZone
from python.utils.enums.colors import Color
from python.utils.enums.translation_keys import TranslationKeys


class Entrance(RegistryMixin[int, "Entrance"]):
    class_id = itertools.count()

    def __init__(self,point1_x: float,point1_y: float,point1_z: float,point1_angel: float,point1_interior: int,point1_vw: int,point2_x: float,point2_y: float,point2_z: float,point2_angel: float,point2_interior: int,point2_vw: int, name: str,  radius: float = 2.0):
        self.id: int = next(Entrance.class_id)
        self.name: str = name
        self.entranceteleport1: EntranceTeleport = EntranceTeleport(point1_x, point1_y, point1_z, point1_angel, point1_interior, point1_vw, radius, self)
        self.entranceteleport2: EntranceTeleport = EntranceTeleport(point2_x, point2_y, point2_z, point2_angel, point2_interior, point2_vw, radius, self)

        Entrance.add_registry_item(self.id, self)

    @override
    def get_id(self) -> int:
        return self.id
 
    def handle_teleport(self, player: Player, teleport_zone: TeleportDynamicZone):
        if player.check_used_teleport():
            return

        if player.have_hospital_time:
            player.send_system_message_multi_lang(Color.RED, TranslationKeys.INHOSPITAL)
            return

        if player.in_vehicle():
            return
        
        if self.entranceteleport1.zone.id == teleport_zone.id:
            teleport: EntranceTeleport = self.entranceteleport2
        
        else:
            teleport: EntranceTeleport = self.entranceteleport1

        sound_id = 1 if teleport.interior != 0 or teleport.vw != 0 else 0

        player.play_sound(sound_id, 0.0, 0.0, 0.0)
        player.set_interior(teleport.interior)
        player.set_virtual_world(teleport.vw)
        player.set_pos(teleport.x, teleport.y, teleport.z)
        player.set_facing_angle(teleport.angel)


class EntranceTeleport:
    def __init__(self, x: float,y: float,z: float,angel: float,interior: int,vw: int,radius: float,entrance: Entrance):
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.angel: float = angel
        self.interior: int = interior
        self.vw: int = vw
        self.radius: float = radius

        self.zone: TeleportDynamicZone = TeleportDynamicZone.create_sphere(self.x, self.y, self.z, self.radius, world_id=self.vw, interior_id=self.interior) # type: ignore
        TeleportDynamicZone.add_registry_item(self.zone.id, self.zone)
        self.zone.entrance = entrance # type: ignore
