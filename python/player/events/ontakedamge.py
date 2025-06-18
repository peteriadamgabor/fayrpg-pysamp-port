from python.model.server import Player
from python.logging.loggers import exception_logger


@exception_logger.catch
@Player.on_take_damage  # type: ignore
@Player.using_registry
def on_take_damage(player: Player, issuer_id: int, amount: float, weapon_id: int, body_part: int):
    if weapon_id == 37:
        weapon = player.weapon()
        if 22 <= weapon <= 42 and weapon != 39 and weapon != 40:
            player.set_armed_weapon(0)

    if body_part == 9:
        player.set_health(0)
    else:
        player.set_health(player.health - amount)
