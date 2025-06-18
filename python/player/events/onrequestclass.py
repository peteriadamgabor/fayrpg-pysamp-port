from pysamp import set_timer
from python.database.context_managger import transactional_session
from python.model.database import Player as PlayerDB
from python.model.server import Player
from python.server.database import PLAYER_SESSION
from python.logging.loggers import exception_logger
from python.utils.enums.colors import Color
from ..functions import set_spawn_camera, handle_player_logon
from sqlalchemy import select
from python.utils.helper.python import fixchars

@exception_logger.catch
@Player.on_request_class # type: ignore
def on_request_class(player: Player, _):
    team: int = 0
    skin: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    a: float = 0.0
    weps = (0, 0) * 3

    player.set_spawn_info(team, skin, x, y, z, a, *weps)
    set_timer(set_spawn_camera, 100, False, player)
    player.toggle_spectating(True)

    registry_player = Player.fiend(player.id)

    if registry_player is not None and registry_player.is_logged_in:
        player.spawn()
        return
        
    with transactional_session(PLAYER_SESSION) as session:
        stmt = select(PlayerDB).where(PlayerDB.name == player.get_name())
        player_data = session.scalars(stmt).first()

        if not player_data:
            player.send_client_message(Color.RED, "(( Nincs ilyen karakter! ))")
            set_timer(player.kick, 150, False)
            return

        if not player_data.is_activated:
            player.send_client_message(Color.RED, "(( Ez a karakter nincs még aktiválva! ))")
            set_timer(player.kick, 150, False)
            return

        player.game_text(fixchars("~b~Betöltés folyamatban..."), 1500, 3)
        set_timer(handle_player_logon, 1500, False, player)

