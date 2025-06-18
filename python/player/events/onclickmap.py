from python.model.server import Player
from python.logging.loggers import exception_logger
from python.utils.helper.function import get_z_coord_from_x_y


@Player.on_click_map # type: ignore
@Player.using_registry
@exception_logger.catch
def on_click_map(player: Player, x: float, y: float, z: float):

    if "maptele" in player.custom_vars:
        g_z: float = get_z_coord_from_x_y(x, y)
        player.set_pos_find_z(x, y, g_z)
