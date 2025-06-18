from python.model.server import Player
from python.logging.loggers import exception_logger, player_chat_logger
from python.utils.enums.colors import Color


@exception_logger.catch
@Player.on_text # type: ignore
@Player.using_registry
def on_text(player: Player, text: str):

    if not player.is_logged_in:
        return
    
    player_chat_logger.info(f"{player.name}: {text}")
    player.broadcast_chat_message(Color.WHITE, text, 30.0)
    return 0
