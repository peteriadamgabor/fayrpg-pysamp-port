from sqlalchemy import select
from python.model.database import Item
from python.server.database import PLAYER_SESSION


def is_valid_item_id(item_id: int) -> bool:
    with PLAYER_SESSION() as session:
        return session.scalars(select(Item).where(Item.id == item_id)).first() is not None
    

def get_item_name(item_id: int) -> str:
    with PLAYER_SESSION() as session:
        return session.scalars(select(Item).where(Item.id == item_id)).one().name
    

def is_stackable_item(item_id: int) -> bool:
    with PLAYER_SESSION() as session:
        return session.scalars(select(Item).where(Item.id == item_id)).one().is_stackable
    
