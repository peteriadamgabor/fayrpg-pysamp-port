from python.model.server import Player
from python.logging.loggers import exception_logger


@exception_logger.catch
@Player.finished_downloading  # type: ignore
@Player.using_registry
def finished_downloading(player: Player, vw: int):
    return 1
