from datetime import datetime

from python.model.server import Player
from python.model.transorm import Transform
from python.logging.loggers import exception_logger
from python.utils.enums.colors import Color
from python.utils.enums.translation_keys import TranslationKeys
from python.utils.globals import HOUSE_VIRTUAL_WORD
from python.utils.helper.python import format_numbers
from ..functions import handle_player_hopital_spawn
from pystreamer import update as streamer_update
from pystreamer import toggle_idle_update as streamer_toggle_idle_update

from python.model.server import House
from python.model.dto import Skin as SkinDTO
from python.model.database import PlayerFine as PlayerFineDB
from python.model.database import Skin as SkinDB

@exception_logger.catch
@Player.on_spawn # type: ignore
@Player.using_registry
def on_spawn(player: Player):

    streamer_update(player.id)
    streamer_toggle_idle_update(player.id, 0)
    streamer_toggle_idle_update(player.id, 1)

    if not player.is_logged_in:
        return

    session_in_played = (datetime.now() - player.login_date).seconds

    player.played_time += session_in_played
    player.today_played += session_in_played
    player.lvl = player.calculate_lvl(int((player.played_time + 1) / 3600))

    player.skin = Transform.get_dto(SkinDB, SkinDTO, getattr(player.skin, 'id'))

    player.set_skin(player.skin.id)

    if player.set_to_back:
        player.back()
        return

    if player.is_dead or player.have_hospital_time:
        player.send_system_message_multi_lang(Color.WHITE, TranslationKeys.SPAWNINHOSPITAL)
        handle_player_hopital_spawn(player)

        if player.is_dead:
            player.is_dead = False
            player.set_health(100)

            fine = player.calculate_hopital_fine()

            PlayerFineDB.create(player.dbid, None, "HF", fine, "Kórházi kezelés költsége")
            player.send_system_message_multi_lang(Color.WHITE, TranslationKeys.DEADMSG, format_numbers(fine))

    else:
        player.set_health(player.health)
        spawn_house: House | None = player.get_spawn_hous()

        if spawn_house:
            player.set_pos(spawn_house.house_type.enter_x, spawn_house.house_type.enter_y, spawn_house.house_type.enter_z)
            player.set_facing_angle(spawn_house.house_type.angle)
            player.set_interior(spawn_house.house_type.interior)
            player.set_virtual_world(HOUSE_VIRTUAL_WORD + spawn_house.id)

        else:
            player.set_pos(1287.3256, -1528.6997, 13.5457)
