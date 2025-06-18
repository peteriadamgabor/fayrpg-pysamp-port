from python.model.server import Player
from python.logging.loggers import exception_logger


@Player.command
@Player.using_registry
@exception_logger.catch
def banyasz(player: Player, main_type: str = ""):
    pass
