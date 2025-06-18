from python.model.server import Vehicle


@Vehicle.on_spawn
@Vehicle.using_registry
def on_spawn(vehicle: Vehicle):
    if not vehicle.is_registered:
        vehicle.destroy()
