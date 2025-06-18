from python.model.server import Player
from python.logging.loggers import exception_logger


@Player.request_download # type: ignore
@Player.using_registry
@exception_logger.catch
def request_download(player: Player, type: int, crc: int):
    return 1