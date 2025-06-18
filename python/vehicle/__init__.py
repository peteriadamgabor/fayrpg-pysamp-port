import atexit

from sqlalchemy import select

from python.database.context_managger import transactional_session
from python.server.database import VEHICLE_SESSION
from python.model.database import Vehicle as VehicleDB
from python.model.server import Vehicle
from python.utils.vars import VEHICLE_PLATE_MAP

from . import events
from . import commands


def init_module():
    """
    This function is called when the module is first loaded.
    """
    print(f"Module {__name__} is being initialized.")
    
    with transactional_session(VEHICLE_SESSION) as session:
        cars = session.scalars(select(VehicleDB)).all()

        for car in cars:
            model_id: int = car.vehicle_model_id + 399
            x: float = car.x
            y: float = car.y
            z: float = car.z
            angle: float = car.angle
            color_1: int = int(car.color_1)
            color_2: int = int(car.color_2)
            db_id = car.id

            veh: Vehicle = Vehicle.create(model_id, x, y, z, angle, color_1, color_2, -1, car.plate, db_id=db_id)
            car.in_game_id = veh.id

            VEHICLE_PLATE_MAP.setdefault(car.plate, veh)


def cleanup_module():
    """
    This function is called when the program is exiting.
    """
    print(f"Module {__name__} is being unloaded.")

    vehicles: list[Vehicle] = list(Vehicle.get_registry_items())

    with transactional_session(VEHICLE_SESSION) as session:
        for vehicle in vehicles:
            if vehicle.is_registered:
                session.scalars(select(VehicleDB).filter(VehicleDB.id == vehicle.db_id)).first().in_game_id = None
                
            vehicle.destroy()

atexit.register(cleanup_module)

init_module()
