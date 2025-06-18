from python.model.server import Player, DynamicZone

@DynamicZone.on_player_leave
@Player.using_registry
def on_player_leave_dynamic_zone(player: Player, dynamic_zone: DynamicZone):
    zone: DynamicZone = DynamicZone.get_registry_item(dynamic_zone.id)

    if not zone:
        return

    if player.in_duty_point:
        player.in_duty_point = False

    player.variables.active_zones.remove(zone)
