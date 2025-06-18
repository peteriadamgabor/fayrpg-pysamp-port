from python.model.server import Player
from python.logging.loggers import exception_logger


@exception_logger.catch
@Player.on_stream_in # type: ignore
@Player.using_registry
def on_stream_in(player: Player, for_player: Player):

    p = Player.get_registry_item(for_player.id)

    if p is not None:
        player.streamed_players.append(p)
