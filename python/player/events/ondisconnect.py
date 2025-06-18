from datetime import datetime
from sqlalchemy import select

from python import LogTypes
from python.database.context_managger import transactional_session
from python.model.database import Player as PlayerDB
from python.model.server import Player
from python.player.functions import clear_player_rent_cars
from python.server.database import MAIN_SESSION
from python.logging import exception_logger, Logger
from python.utils.enums.colors import Color
from python.utils.vars import ADMIN_PLAYERS


@exception_logger.catch
@Player.on_disconnect # type: ignore
def on_disconnect(player: Player, reason: int):

    reason_txt: str

    match (reason):
        case 0:
            reason_txt = "Timeout/Crash"
        case 1:
            reason_txt = "Quit"
        case 2:
            reason_txt = "Kick/Ban"
        case _: 
            reason_txt = "Ismeretlen"

    log_msg: str = f"{player.get_name()} lecsatlakozott a szerverről. Indok: {reason_txt} IP: {player.get_ip()}"
    Logger.write_log(LogTypes.CONNECTION, log_msg, player.session_token)

    registry_player = Player.get_registry_item(player.id)
    Player.remove_from_registry(player)

    if registry_player is None or not registry_player.is_logged_in:
        return
    
    registry_player.broadcast_system_message(Color.ORANGE, f"{player.name} kilépett! Indok: {reason_txt}", 7.0)

    session_in_played = (datetime.now() - registry_player.login_date).seconds

    registry_player.played_time += session_in_played
    registry_player.today_played += session_in_played

    clear_player_rent_cars(registry_player)

    if registry_player.have_hospital_time:
        registry_player.hospital_time = (registry_player.hospital_release_date - datetime.now()).total_seconds()
    else:
        registry_player.hospital_time = 0

    if registry_player.role:
        ADMIN_PLAYERS.pop(registry_player.id)

    registry_player.kill_timers()

    registry_player.update_database_entity(is_force_update=True)

    with transactional_session(MAIN_SESSION) as session:
        stmt = select(PlayerDB).where(PlayerDB.id == registry_player.dbid)
        player_data = session.scalars(stmt).one()
        player_data.in_game_id = -1
