from python.model.server import Player
from python.model.server import Vehicle
from python.logging.loggers import exception_logger
from python.utils.enums.states import State



@exception_logger.catch
@Player.on_state_change  # type: ignore
@Player.using_registry
def on_state_change(player: Player, new_state: int, old_state: int):
    if old_state == State.ON_FOOT and (new_state == State.DRIVER or new_state == State.PASSENGER):
        vehid = player.get_vehicle_id()

        vehicle: Vehicle = Vehicle.get_registry_item(vehid)

        if vehicle:
            vehicle.skip_check_damage = True
            vehicle.add_passenger(player)
            vehicle.log_passenger_activity(player.name, player.get_vehicle_seat())
 

        if new_state == State.DRIVER:
            player.show_speedo()
                
