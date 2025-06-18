from python.jobs.crab_fisherman.events import remove_icon_cages
from python.model.server import Player
from python.model.server import Vehicle
from python.logging.loggers import exception_logger


@exception_logger.catch
@Player.on_exit_vehicle  # type: ignore
@Player.using_registry
def on_exit_vehicle(player: Player, vehicle: Vehicle):
    vehicle = Vehicle.get_registry_item(int(vehicle.id))

    if vehicle:
        vehicle.remove_passenger(player)
        vehicle.skip_check_damage = True
        remove_icon_cages(player, vehicle)

        player.destroy_speedo()
