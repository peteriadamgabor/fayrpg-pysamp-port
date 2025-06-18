from pysamp import set_timer
from python.model.server import Player
from python.model.server import Vehicle
from python.vehicle.functions import reload_vehicle


@Vehicle.on_death
@Vehicle.using_registry
def on_death(vehicle: Vehicle, killer: Player):
    if vehicle.is_registered:
        vehicle.update_panels_damage(3, 3, 3, 3, 3, 3, 3)
        vehicle.update_doors_damage(4, 4, 4, 4)
        vehicle.update_lights_damage(1, 1, 1)
        vehicle.update_tires_damage(1, 1, 1, 1)
        vehicle.health = 250.0

        set_timer(reload_vehicle, 2000, False, vehicle.db_id)
        
    vehicle.destroy()
