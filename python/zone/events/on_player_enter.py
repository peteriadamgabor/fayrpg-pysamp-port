from python.model.server import DutyPointDynamicZone
from python.model.server import Player, DynamicZone, Business, TeleportDynamicZone
from python.model.server import InteriortDynamicZone
from python.utils.globals import BUESSNES_VIRTUAL_WORD


@DynamicZone.on_player_enter # type: ignore
@Player.using_registry
def on_player_enter_dynamic_zone(player: Player, dynamic_zone: DynamicZone):
    unknow_zone = DynamicZone.get_registry_item(dynamic_zone.id)

    if not unknow_zone:
        return
    
    player.variables.active_zones.append(unknow_zone) # type: ignore

    match unknow_zone:
        case TeleportDynamicZone() as teleport_zone:
            teleport_zone.entrance.handle_teleport(player, teleport_zone)

        case DutyPointDynamicZone() as dutypoint_zone:
            if player.fraction is not None and not player.in_vehicle() and dutypoint_zone.duty_point.fraction.id == player.fraction.id:
                player.in_duty_point = True

        case InteriortDynamicZone():
            if not player.check_used_teleport() and not player.in_vehicle() and player.get_virtual_world() >= BUESSNES_VIRTUAL_WORD:
                business = Business.get_registry_item(player.get_virtual_world() - BUESSNES_VIRTUAL_WORD)
                if business is not None:
                    business.exit_player(player)
