import atexit

from sqlalchemy import select

from python.database.context_managger import transactional_session

from python.server.database import HOUSE_SESSION

from python.model.database import House as HouseDB
from python.model.server import House
from python.model.dto import Player as PlayerDTO
from python.model.dto import HouseType as HouseTypeDTO
from python.model.transorm import Transform

from . import events
from . import commands


def init_module():
    print(f"Module {__name__} is being initialized.")
    
    with transactional_session(HOUSE_SESSION) as session:
        houses: list[HouseDB] = list(session.scalars(select(HouseDB)).all())

        for house in houses:
            owner: PlayerDTO = Transform.convert_db_to_dto(house.owner, PlayerDTO)
            house_type: HouseTypeDTO = Transform.convert_db_to_dto(house.house_type, HouseTypeDTO)

            House(house.id,
                  house.entry_x,
                  house.entry_y,
                  house.entry_z,
                  house.angle,
                  house.type,
                  house.locked,
                  house.price,
                  house.rent_date,
                  owner,
                  house_type,
                  house.is_spawn,
                  house.is_robbed,
                  house.lockpick_time,
                  house.alarm_lvl,
                  house.door_lvl)


def unload_module():
    """
    This function is called when the program is exiting.
    """
    print(f"Module {__name__} is being unloaded.")
   

atexit.register(unload_module)

init_module()
