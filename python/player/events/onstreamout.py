from python.model.server import Player
from python.logging.loggers import exception_logger


@exception_logger.catch
@Player.on_stream_out  # type: ignore
@Player.using_registry
def on_stream_out(player: Player, for_player: Player):
    for i, p in enumerate(player.streamed_players):
        if p.id == for_player.id:
            del player.streamed_players[i]
