import atexit

from sqlalchemy import select

from python.database.context_managger import transactional_session

from python.server.database import VEHICLE_SESSION

from python.model.database import Business as BusinessDB
from python.model.database import Player as PlayerDB
from python.model.server import Business
from python.model.dto import Player as PlayerDTO
from python.model.dto import BusinessType as BusinessTypeDTO
from python.model.dto import Interior as InteriorDTO
from python.model.transorm import Transform

from . import events
from . import commands


def init_module():
    print(f"Module {__name__} is being initialized.")
    
    with transactional_session(VEHICLE_SESSION) as session:
        businesses: list[BusinessDB] = list(session.scalars(select(BusinessDB).join(PlayerDB, isouter = True )).all())
        for business in businesses:

            business_type: BusinessTypeDTO = Transform.convert_db_to_dto(business.business_type, BusinessTypeDTO)
            interior: InteriorDTO = Transform.convert_db_to_dto(business.interior, InteriorDTO)
            owner: PlayerDTO = Transform.convert_db_to_dto(business.owner, PlayerDTO, True)

            Business(business.id, 
                     business_type, 
                     interior, 
                     owner, 
                     business.price, 
                     business.name, 
                     business.x, 
                     business.y, 
                     business.z, 
                     business.a, 
                     business.load_x, 
                     business.load_y, 
                     business.load_z, 
                     business.load_a, 
                     business.locked, 
                     business.company_chain,
                     business.is_illegal)


def unload_module():
    """
    This function is called when the program is exiting.
    """
    print(f"Module {__name__} is being unloaded.")
   

atexit.register(unload_module)

init_module()
