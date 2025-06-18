from typing import Any

from python.model.server import Player
from python.logging.loggers import exception_logger


@exception_logger.catch
@Player.on_weapon_shot # type: ignore
@Player.using_registry
def on_weapon_shot(player: Player, weapon_id: int, hit_type: Any, x: float, y: float, z: float):
    pass
