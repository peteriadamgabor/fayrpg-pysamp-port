from python.business.events import on_player_pick_up_pickup_business
from python.house.events import on_player_pick_up_pickup_house
from python.model.server import Player
from python.model.server import DynamicPickup
from python.model.server import HousePickup
from python.model.server import BusinessPickup

@DynamicPickup.on_player_pick_up  # type: ignore
@Player.using_registry
def dynamic_pickup_on_pick_up_pickup(player: Player, pickup: DynamicPickup):
    if player.is_block_pickup_pickup():
        return True
    
    unknow_pickup = DynamicPickup.get_registry_item(pickup.id)

    if isinstance(unknow_pickup, HousePickup):
        house_pickup: HousePickup = unknow_pickup
        on_player_pick_up_pickup_house(player, house_pickup.house)

    elif isinstance(unknow_pickup, BusinessPickup):
        buiness_pickup: BusinessPickup = unknow_pickup
        on_player_pick_up_pickup_business(player, buiness_pickup.business)

    return True
