from typing import Optional, override

from sqlalchemy import select
from pystreamer.dynamictextlabel import DynamicTextLabel

from python.utils.enums.colors import Color
from python.server.database import BUSINESS_SESSION

from python.database import transactional_session 

from python.model.transorm import Transform
from python.model.registrymixin import RegistryMixin
from python.model.attribute_monitor import AttributeMonitor

from python.model.database import Player as PlayerDB
from python.model.database import Interior as InteriorDB
from python.model.database import Business as BusinessDB
from python.model.database import BusinessType as BusinessTypeDB
from python.model.database import ShopItem as ShopItemDB
from python.model.database import ShopCar as ShopCarDB

from python.model.server.business_pickup import BusinessPickup

from python.model.server import Player

from python.model.dto import Player as PlayerDTO
from python.model.dto import Interior as InteriorDTO
from python.model.dto import BusinessType as BusinessTypeDTO
from python.model.dto import ShopItem as ShopItemDTO
from python.model.dto import ShopCar as ShopCarDTO

class Business(RegistryMixin[int, "Business"], AttributeMonitor):
    def __init__(self, id: int,
                 business_type: BusinessTypeDTO,
                 interior: InteriorDTO, 
                 owner: PlayerDTO, 
                 price: int, 
                 name: str,
                 x: float, 
                 y: float,
                 z: float,
                 a: float,
                 load_x: float,
                 load_y: float,
                 load_z: float,
                 load_a: float,
                 locked: bool,
                 company_chain: int,
                 is_illegal: bool):
        AttributeMonitor.__init__(self, {"interior", "owner", "x", "y", "z", "a", "locked"})
        
        self.id: int = id
        self.business_type: Optional[BusinessTypeDTO] = business_type
        self.interior: Optional[InteriorDTO] = interior
        self.owner: Optional[PlayerDTO] =  owner
        self.price: int =  price
        self.name: str = name
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.a: float = a
        self.load_x: float = load_x
        self.load_y: float = load_y
        self.load_z: float = load_z
        self.load_a: float = load_a
        self.locked: bool = locked
        self.company_chain: int = company_chain
        self.is_illegal: bool = is_illegal
        self.itmes: list[ShopItemDTO] = []
        self.cars: list[ShopCarDTO] = []

        self.label: DynamicTextLabel = DynamicTextLabel.create(name, Color.WHITE, x, y, z + 0.6, 25.0)
        self.pickup: BusinessPickup = BusinessPickup.create(1274, 1, x, y, z, 0, 0)
        self.pickup.set_business(self)

        self.update_shop_items()

        BusinessPickup.add_registry_item(self.pickup.id, self.pickup)

        self.add_registry_item(self.id, self)

    @override
    def get_id(self) -> int:
        return self.id

    def update_shop_items(self):
        with transactional_session(BUSINESS_SESSION) as session:
            entity: BusinessDB = session.scalars(select(BusinessDB).where(BusinessDB.id == self.id)).one()
            self.itmes = [Transform.get_dto(ShopItemDB, ShopItemDTO, -1, filter=((ShopItemDB.item_id == i.item_id) & (ShopItemDB.business_id == self.id))) for i in entity.items]
            self.cars = [Transform.get_dto(ShopCarDB, ShopCarDTO, -1, filter=((ShopCarDB.vehicle_model_id == i.vehicle_model_id) & (ShopCarDB.business_id == self.id))) for i in entity.cars]

    @override
    def update_database_entity(self, is_force_update: bool = False) -> None:
        if not self.attr_change and not is_force_update:
            return
        
        try:
            with transactional_session(BUSINESS_SESSION) as session:
                entity = session.scalars(select(BusinessDB).where(BusinessDB.id == self.id)).one()

                entity.price = self.price
                entity.name = self.name
                entity.x = self.x
                entity.y = self.y
                entity.z = self.z
                entity.a = self.a
                entity.locked = self.locked
                entity.company_chain = self.company_chain
                entity.is_illegal = self.is_illegal

                entity.business_type = Transform.get_db(BusinessTypeDB, getattr(self.business_type, 'id', None), existing_session=session)
                entity.interior = Transform.get_db(InteriorDB, getattr(self.interior, 'id', None), existing_session=session)
                entity.owner = Transform.get_db(PlayerDB, getattr(self.owner, 'id', None), existing_session=session)

        except Exception as e:
            print(e)
            pass

        finally:
            self.attr_change = False

    def move(self, x: float, y: float, z: float, a: float) -> bool:
        try:
            self.x = x
            self.y = y
            self.z = z
            self.a = a

            self.label.destroy()
            self.pickup.destroy()

            self.label: DynamicTextLabel = DynamicTextLabel.create(self.name, Color.WHITE, x, y, z + 0.6, 25.0)
            self.pickup: BusinessPickup = BusinessPickup.create(1274, 1, x, y, z, 0, 0)
            self.pickup.set_business(self)

            return True
        
        except Exception as e:
            print(e)
            return False

    def exit_player(self, player: Player):
        player.play_sound(0, 0.0, 0.0, 0.0)
        player.set_pos(self.x, self.y, self.z)
        player.set_facing_angle(self.a) 
        player.set_interior(0)
        player.set_virtual_world(0)