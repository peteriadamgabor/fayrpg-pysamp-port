from . import shared
from . import lawenforcement

import atexit

from sqlalchemy import select

from python.database.context_managger import transactional_session

from python.server.database import MAIN_SESSION

from python.model.database import Fraction as FractionDB
from python.model.dto import Fraction as FractionDTO
from python.model.dto import Division as DivisionDTO
from python.model.dto import Skin as SkinDTO
from python.model.dto import Rank as RankDTO

from python.model.transorm import Transform

def init_module():
    print(f"Module {__name__} is being initialized.")
    
    with transactional_session(MAIN_SESSION) as session:
        fractions: list[FractionDB] = list(session.scalars(select(FractionDB)).all())

        for fraction in fractions:

            divisions: list[DivisionDTO] = [Transform.convert_db_to_dto(division, DivisionDTO) for division in fraction.divisions]
            skins: list[SkinDTO] = [Transform.convert_db_to_dto(skin, SkinDTO) for skin in fraction.skins]
            ranks: list[RankDTO] = [RankDTO(id=rank.id, order=rank.order, fraction_id=rank.fraction.id, division_id=getattr(rank.division, "id", None), name=rank.name) for rank in fraction.ranks]

            FractionDTO(id=fraction.id,
                        name=fraction.name,
                        acronym=fraction.acronym,
                        duty_everywhere=fraction.duty_everywhere,
                        skins=skins,
                        divisions=divisions,
                        ranks=ranks,
                        type=fraction.type)
        
        
def unload_module():
    """
    This function is called when the program is exiting.
    """
    print(f"Module {__name__} is being unloaded.")
   

atexit.register(unload_module)

init_module()
