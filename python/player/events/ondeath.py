from datetime import datetime
from datetime import timedelta

from python.utils.enums.log_type import LogTypes
from python.logging import Logger, exception_logger
from python.model.server import Player
from python.utils.helper.function import get_weapon_name


@exception_logger.catch
@Player.on_death # type: ignore # noqa
@Player.using_registry
def on_death(player: Player, issuer_id: int, weapon_id: int):
    player.is_dead = True
    player.set_to_back = False
    player.dead_by_weapon_id = weapon_id

    sec = (15 * 60)

    player.hospital_time = sec
    player.hospital_release_date = datetime.now() + timedelta(0, sec)

    killer = Player.get_registry_item(issuer_id)

    if killer is not None:
        log_msg = f"{player.name}-t megölte {killer.name}. Fegyver: {get_weapon_name(weapon_id)}"
        additional_data = {
            "interior": player.interior,
            "virtual_world": player.virtual_world,
            "dead_player_x": player.x,
            "dead_player_y": player.y,
            "dead_player_z": player.z,
            "dead_player_a": player.a,
            "killer_player_x": killer.x,
            "killer_player_y": killer.y,
            "killer_player_z": killer.z,
            "killer_session_token": killer.session_token,
        }

    else:
        if weapon_id == 255:
            log_msg = f"{player.name}-t öngyilkos lett (vagy megölte egy admin)"
        else:
            log_msg = f"{player.name}-t meghalt. Indok: {get_weapon_name(weapon_id)}"

        additional_data = {
            "interior": player.interior,
            "virtual_world": player.virtual_world,
            "dead_player_x": player.x,
            "dead_player_y": player.y,
            "dead_player_z": player.z,
            "dead_player_a": player.a,
        }

    Logger.write_log(LogTypes.KILL, log_msg, player.session_token, additional_data)
