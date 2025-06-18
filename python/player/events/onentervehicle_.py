from python.jobs.crab_fisherman.events import show_icon_cages
from python.model.server import Player
from python.model.server import Vehicle
from python.logging.loggers import exception_logger

@exception_logger.catch
@Player.on_enter_vehicle # type: ignore
@Player.using_registry
def on_enter_vehicle(player: Player, vehicle: Vehicle, is_passenger: bool):
    vehicle = Vehicle.get_registry_item(int(vehicle.id))

    if vehicle:
        show_icon_cages(player, vehicle)
