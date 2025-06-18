from typing import override
from datetime import datetime
from sqlalchemy import select

from pysamp import set_timer

from pystreamer.dynamictextlabel import DynamicTextLabel

from python.database.context_managger import transactional_session

from python.server.database import HOUSE_SESSION

from python.model.transorm import Transform
from python.model.registrymixin import RegistryMixin
from python.model.attribute_monitor import AttributeMonitor

from python.model.dto import Player as PlayerDTO
from python.model.dto import HouseType as HouseTypeDTO

from python.model.database import House as HouseDB
from python.model.database import Player as PlayerDB
from python.model.database import HouseType as HouseTypeDB


from python.utils.enums.colors import Color
from python.utils.globals import HOUSE_VIRTUAL_WORD

from .house_pickup import HousePickup


class House(RegistryMixin[int, "Player"], AttributeMonitor):

    @classmethod
    def get_by_virtual_word(cls, vw: int) -> "House":
        return cls.get_registry_item(vw - HOUSE_VIRTUAL_WORD)


    def __init__(self, id: int, entry_x: float, entry_y: float, entry_z: float, angle: float, type: int, locked: bool,
                 price: int, rent_date: datetime, owner: PlayerDTO, house_type: HouseTypeDTO, is_spawn: bool,
                 is_robbed: bool, lockpick_time: int, alarm_lvl: int, door_lvl: int):

        super().__init__()
        AttributeMonitor.__init__(self, { "locked", "entry_x", "entry_y", "entry_z", "angle",
                                         "owner", "is_robbed", "lockpick_time", "alarm_lvl",
                                         "door_lvl" })

        self.id: int = id

        if owner:
            self.__pickup_model: int = 1239
        else:
            self.__pickup_model: int = 1273 if type == 0 else 1272

        self.type: int = type
        self.price: int = price
        self.entry_x: float = entry_x
        self.entry_y: float = entry_y
        self.entry_z: float = entry_z
        self.angle: float = angle
        self.locked: bool = locked
        self.is_spawn: bool = is_spawn
        self.rent_date: datetime = rent_date
        self.owner: PlayerDTO = owner
        self.house_type: HouseTypeDTO = house_type
        self.is_robbed: bool = is_robbed
        self.lockpick_time: int = lockpick_time
        self.alarm_lvl: int = alarm_lvl
        self.door_lvl: int = door_lvl
        self.is_alarmed: bool = False

        self.pickup: HousePickup = HousePickup.create(self.__pickup_model, 1, self.entry_x, self.entry_y, self.entry_z, 0, 0)
        self.pickup.set_house(self)

        self.update_timer = set_timer(self.update_database_entity, 5 * 1_000 * 60, True)

        HousePickup.add_registry_item(self.pickup.id, self.pickup)

        self.label: DynamicTextLabel = DynamicTextLabel.create(f"Házszám: {self.id}", Color.LABEL_RED,
                                                                 self.entry_x, self.entry_y, self.entry_z + 0.6,
                                                                 25.0)

        self.add_registry_item(self.id, self)


    @override
    def get_id(self) -> int:
        return self.id


    @override
    def update_database_entity(self, is_force_update: bool = False) -> None:
        if not self.attr_change and not is_force_update:
            return

        try:
            with transactional_session(HOUSE_SESSION) as session:
                house_db = session.scalars(select(HouseDB).where(HouseDB.id == self.id)).one()

                house_db.entry_x = self.entry_x
                house_db.entry_y = self.entry_y
                house_db.entry_z = self.entry_z
                house_db.angle = self.angle
                house_db.type = self.type
                house_db.locked = self.locked
                house_db.price = self.price
                house_db.rent_date = self.rent_date
                house_db.is_spawn = self.is_spawn
                house_db.is_robbed = self.is_robbed
                house_db.lockpick_time = self.lockpick_time
                house_db.door_lvl = self.door_lvl

                house_db.owner = Transform.get_db(PlayerDB, getattr(self.owner, 'id', None), existing_session=session)
                house_db.house_type = Transform.get_db(HouseTypeDB, getattr(self.house_type, 'id', None), existing_session=session)

        except Exception as e:
            print(e)
            pass

        finally:
            self.attr_change = False


    def refresh_pickup(self, model: int):
        self.pickup.destroy()
        self.pickup: HousePickup = HousePickup.create(model, 1, self.entry_x, self.entry_y, self.entry_z, 0, 0)
        self.pickup.set_house(self)
