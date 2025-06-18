from python.model.server import Player
from python.model.server import Vehicle
from python.logging.loggers import exception_logger
from python.utils.enums.states import State
from python.vehicle.functions import player_in_car_handler
from ..functions import handle_fly_mode

@exception_logger.catch
@Player.on_update  # type: ignore
@Player.using_registry
def on_update(player: Player):

    if not player.is_logged_in:
        return
    
    if "fly_mode" in player.custom_vars:
        handle_fly_mode(player)

    if player.last_state != player.get_state():
        if player.last_state == State.DRIVER:
            player.destroy_speedo()

        player.last_state = State(player.get_state())

    vehicle: Vehicle = player.get_vehicle()

    if vehicle:
        player_in_car_handler(player, vehicle)
        
