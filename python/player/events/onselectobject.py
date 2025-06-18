from pystreamer import edit_dynamic_object
from python.model.server import Player
from python.model.server import Map
from python.logging.loggers import exception_logger



@exception_logger.catch
@Player.on_select_object # type: ignore
@Player.using_registry
def on_select_object(player: Player, type: int, objectid: int, modelid: int, x: float, y: float, z: float):

    # static_objects
    # dynamic_objects

    for value in Map.get_registry_items():
        if type == 1:
            for static in value.static_objects:
                if static.id == objectid:
                    player.edit_object(static.id)

        else:
            for dynamic in value.dynamic_objects:
                if dynamic.id == objectid:
                    edit_dynamic_object(player.id, dynamic.id)
