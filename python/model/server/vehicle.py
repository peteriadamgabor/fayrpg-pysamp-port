import datetime
import math


from samp import CallRemoteFunction  # type: ignore

from sqlalchemy import select
from typing import Any, override, Optional

from pysamp import set_timer, kill_timer, call_native_function
from pysamp.player import Player
from pysamp.vehicle import Vehicle as BaseVehicle
from pystreamer.dynamicmapicon import DynamicMapIcon

from python.model.transorm import Transform
from python.model.registrymixin import RegistryMixin
from python.model.attribute_monitor import AttributeMonitor

from python.model.database import Vehicle as VehicleDB
from python.model.database import FuelType as FuelTypeDB
from python.model.database import Fraction as FractionDB
from python.model.database import VehicleModel as VehicleModelDB

from python.model.dto import FuelType as FuelTypeDTO
from python.model.dto import Fraction as FractionDTO
from python.model.dto import VehicleModel as VehicleModelDTO
from python.model.dto import Player as PlayerDTO

from python.database import transactional_session
from python.server.database import VEHICLE_SESSION, UTIL_SESSION


class Vehicle(BaseVehicle, RegistryMixin[int, "Vehicle"], AttributeMonitor):

    @classmethod
    def get_model_id_by_name(cls, name: str) -> int | None:
        with transactional_session(UTIL_SESSION) as session:
            model_id: int | None = session.scalars(
                select(VehicleModelDB.id + 399).filter(VehicleModelDB.name.ilike(f"%{name}%"))).first()
            return model_id


    def __init__(self, id: int, db_id: int = None, color_1: int = 0, color_2: int = 1, plate: str = ""):
        super().__init__(id)
        AttributeMonitor.__init__(self, {"locked", "x", "y", "z", "angle", "health", "distance" })

        self.under_init = True

        self.db_id: int = db_id
        self.color_1: int = color_1
        self.color_2: int = color_2
        self.health: float = 1000
        self.is_starting: bool = False
        self.is_registered: bool = False
        self.skip_check_damage: bool = False
        self.fix_veh: bool = False
        self.action_lock: bool = False
        self.is_loaded: bool = False
        self.panels_damage_bit: int = 0
        self.doors_damage_bit: int = 0
        self.lights_damage_bit: int = 0
        self.tires_damage_bit: int = 0
        self.passengers: set = set()
        self.passenger_activity: list[str] = []
        self.plate: str = plate
        self.custom_vars: dict[str, Any] = {}
        self.timers: dict[str, Any] = {}

        self.model: VehicleModelDTO = Transform.get_dto(VehicleModelDB, VehicleModelDTO, self.get_model() - 399)
        self.last_pos: tuple[float, float, float] = self.get_position()
        self.limiter: float = 0
        self.is_rented: bool = False
        self.rent_started: Optional[datetime] = None
        self.rent_end: Optional[datetime] = None
        self.renter: Optional["Player"] = None
        self.fraction: Optional[FractionDTO] = None

        self.distance: int = 0
        self.patrol_name: str = ""

        self.set_params_ex(0,0,0,0,0,0,0)
        
        with transactional_session(VEHICLE_SESSION) as session:
            vehicle_obj: VehicleDB = session.scalars(select(VehicleDB).where(VehicleDB.id == self.db_id)).one_or_none()
            if vehicle_obj:
                self.is_registered = True

                self.in_game_id: int = self.id
                self.x: float = vehicle_obj.x
                self.y: float = vehicle_obj.y
                self.z: float = vehicle_obj.z
                self.angle: float = vehicle_obj.angle
                self.color_1: int = vehicle_obj.color_1
                self.color_2: int = vehicle_obj.color_2
                self.owner: PlayerDTO = Transform.convert_db_to_dto(vehicle_obj.owner, PlayerDTO)
                self.fuel_type: FuelTypeDTO = Transform.convert_db_to_dto(vehicle_obj.fuel_type, FuelTypeDTO)
                self.fill_type: FuelTypeDTO = Transform.convert_db_to_dto(vehicle_obj.fill_type, FuelTypeDTO)
                self.fuel_level: float = vehicle_obj.fuel_level
                self.locked: bool = vehicle_obj.locked
                self.health: float = vehicle_obj.health
                self.plate: str = vehicle_obj.plate
                self.distance: int = vehicle_obj.distance
                self.panels_damage: int = vehicle_obj.panels_damage
                self.doors_damage: int = vehicle_obj.doors_damage
                self.lights_damage: int = vehicle_obj.lights_damage
                self.tires_damage: int = vehicle_obj.tires_damage
                self.job_id: int = vehicle_obj.job_id

                self.fraction: FractionDTO = FractionDTO.get_registry_item(vehicle_obj.fraction_id)

                self.is_rentable: bool = vehicle_obj.is_rentabel
                self.rent_price: int = vehicle_obj.rent_price
                self.rent_time: int = vehicle_obj.rent_time

                self.set_damage_status(self.panels_damage, self.doors_damage, self.lights_damage, self.tires_damage)
                self.set_health(self.health if self.health > 250.0 else 250.0)

                self.timers["update_database_entity"] = set_timer(self.update_database_entity, (2 * 60 * 1000), True)

            self.under_init = False

    @classmethod
    def create(cls,model: int, x: float, y: float, z: float, rotation: float,
               color1: int, color2: int, respawn_delay: int, plate: str,
               add_siren: bool = False, db_id: int = None) -> "Vehicle": #type: ignore

        py_samp_veh = super().create(model, x, y, z, rotation, color1, color2, respawn_delay, add_siren)

        new_vehicle = cls(py_samp_veh.id, db_id, color1, color2, plate)
        new_vehicle.set_number_plate(plate)

        Vehicle.add_registry_item(new_vehicle.id, new_vehicle)
        return new_vehicle


    # region functions

    @override
    def update_database_entity(self, is_force_update: bool = False) -> None:
        if (not self.attr_change and not is_force_update) or self.under_init:
            return
        try:
            with transactional_session(VEHICLE_SESSION) as session:
                vehicle_db: VehicleDB = session.scalars(select(VehicleDB).where(VehicleDB.id == self.db_id)).one_or_none()

                if vehicle_db is None:
                    return

                vehicle_db.x = self.x
                vehicle_db.y = self.y
                vehicle_db.z = self.z
                vehicle_db.angle = self.angle
                vehicle_db.color_1 = self.color_1
                vehicle_db.color_2 = self.color_2
                vehicle_db.plate = self.plate
                vehicle_db.health = self.health
                vehicle_db.fuel_level = self.fuel_level
                vehicle_db.locked = self.locked
                vehicle_db.distance = self.distance

                vehicle_db.fuel_type = Transform.get_db(FuelTypeDB, getattr(self.fuel_type, 'id', None), existing_session=session)
                vehicle_db.fill_type = Transform.get_db(FuelTypeDB, getattr(self.fill_type, 'id', None), existing_session=session)
                vehicle_db.fraction = Transform.get_db(FractionDB, getattr(self.fraction, 'id', None), existing_session=session)
                vehicle_db.model = Transform.get_db(VehicleModelDB, getattr(self.model, 'id', None), existing_session=session)

        except Exception as e:
            print(e)
            pass

        finally:
            self.attr_change = False

    @override
    def get_id(self) -> int:
        return self.id


    @override
    def destroy(self) -> bool:
        self.remove_from_registry(self)
        return super().destroy()

    # region property


    def set_action_lock(self, value: bool):
        self.action_lock = value


    def set_fix_veh(self, value: bool):
        self.fix_veh = value


    def is_two_wheels(self):
        return self.model.id in [448, 461, 462, 463, 468, 481, 471, 509, 510, 521, 522, 523, 581, 586]


    def add_passenger(self, passenger):
        self.passengers.add(passenger)


    def remove_passenger(self, passenger):
        self.passengers.remove(passenger)


    def log_passenger_activity(self, passenger, seat):

        if seat == 128:
            return

        match seat:
            case 0:
                seat_name = "sofőr ülés"
            case 1:
                seat_name = "anyos ülés"
            case 2:
                seat_name = "bal hatso ülés"
            case 3:
                seat_name = "jobb hatso ülés"
            case _:
                seat_name = "egyébb ülés"

        self.passenger_activity.append(
            f"{datetime.datetime.now(datetime.UTC).strftime('%Y. %m. %d. %H:%M:%S')} (UTC) - {passenger} - {seat_name}")


    def get_passenger_activity(self):
        return self.passenger_activity

    @property
    def engine(self):
        engine, _, _, _, _, _, _ = self.get_params_ex()
        return engine


    @engine.setter
    def engine(self, value: int):
        _, lights, alarm, doors, bonnet, boot, objective = self.get_params_ex()
        self.set_params_ex(value, lights, alarm, doors, bonnet, boot, objective)


    @property
    def lights(self):
        _, lights, _, _, _, _, _ = self.get_params_ex()
        return lights


    @lights.setter
    def lights(self, value: int):
        engine, _, alarm, doors, bonnet, boot, objective = self.get_params_ex()
        self.set_params_ex(engine, value, alarm, doors, bonnet, boot, objective)


    @property
    def alarm(self):
        _, _, alarm, _, _, _, _ = self.get_params_ex()
        return alarm


    @alarm.setter
    def alarm(self, value: int):
        engine, lights, _, doors, bonnet, boot, objective = self.get_params_ex()
        self.set_params_ex(engine, lights, value, doors, bonnet, boot, objective)


    @property
    def doors(self):
        _, _, _, doors, _, _, _ = self.get_params_ex()
        return doors


    @doors.setter
    def doors(self, value: int):
        engine, lights, alarm, _, bonnet, boot, objective = self.get_params_ex()
        self.set_params_ex(engine, lights, alarm, value, bonnet, boot, objective)


    @property
    def hood(self):
        _, _, _, _, bonnet, _, _ = self.get_params_ex()
        return bonnet


    @hood.setter
    def hood(self, value: int):
        engine, lights, alarm, doors, _, boot, objective = self.get_params_ex()
        self.set_params_ex(engine, lights, alarm, doors, value, boot, objective)


    @property
    def trunk(self):
        _, _, _, _, _, boot, _ = self.get_params_ex()
        return boot


    @trunk.setter
    def trunk(self, value: int):
        engine, lights, alarm, doors, bonnet, _, objective = self.get_params_ex()
        self.set_params_ex(engine, lights, alarm, doors, bonnet, value, objective)

    # endregion

    # region functions

    def set_patrol(self, *name: str) -> int:
        timer: int | None = self.timers.get("patrol_timer", None)

        if timer is not None or self.patrol_name != "":
            kill_timer(timer)
            del self.timers["patrol_timer"]

            self.patrol_name = ""
            for player in self.fraction.duty_players:
                player.map_icons[f"patrol_{self.patrol_name}"].destroy()

            return 0

        concat_name = " ".join(name)

        if concat_name == "":
            return 2

        self.timers["patrol_timer"] = set_timer(self.__update_patrol_icon, (2 * 1000), True)
        self.patrol_name = concat_name
        self.fraction.patrols.append(concat_name)
        return 1


    def __update_patrol_icon(self):
        for player in self.fraction.duty_players:
            x,y,z = self.get_position()
            map_icon: DynamicMapIcon | None = player.map_icons.get(f"patrol_{self.patrol_name}", None)

            if map_icon is None:
                player.map_icons[f"patrol_{self.patrol_name}"] = DynamicMapIcon.create(x, y, z, 0, 0x000096FF, 0,0, player.id, 2500.0, 1)

            else:
                player.map_icons[f"patrol_{self.patrol_name}"].destroy()
                player.map_icons[f"patrol_{self.patrol_name}"] = DynamicMapIcon.create(x, y, z, 0, 0x000096FF, 0,0, player.id, 2500.0, 1)


    def update_damage(self):

        panels, doors, lights, tires = self.get_damage_status()

        if (self.panels_damage_bit == panels
                and self.doors_damage_bit == doors
                and self.lights_damage_bit == lights
                and self.tires_damage_bit == tires):
            return

        if self.db_id is not None:
            with transactional_session(VEHICLE_SESSION) as session:
                vehicle_data: VehicleDB = session.query(VehicleDB).filter(VehicleDB.id == self.db_id).first()

                vehicle_data.panels_damage = panels
                vehicle_data.doors_damage = doors
                vehicle_data.lights_damage = lights
                vehicle_data.tires_damage = tires

        self.panels_damage_bit = panels
        self.doors_damage_bit = doors
        self.lights_damage_bit = lights
        self.tires_damage_bit = tires


    def load_damage(self):
        self.set_damage_status(self.panels_damage_bit,
                               self.doors_damage_bit,
                               self.lights_damage_bit,
                               self.tires_damage_bit)
        self.update_damage()


    def get_panels_damage(self):
        return decode_panels(self.panels_damage_bit)


    def get_doors_damage(self):
        return decode_doors(self.doors_damage_bit)


    def get_lights_damage(self):
        return decode_lights(self.lights_damage_bit)


    def get_tires_damage(self):
        return decode_tires(self.tires_damage_bit)


    def is_driving_backwards(self) -> bool:
        velocity_x, velocity_y, _ = self.get_velocity()
        a: float = self.get_z_angle()

        if a < 90: 
            return velocity_x > 0 > velocity_y

        if a < 180: 
            return  velocity_x > 0 and velocity_y > 0

        if a < 270: 
            return velocity_x < 0 < velocity_y

        return  velocity_x < 0 and velocity_y < 0
    

    def get_speed(self) -> int:
        velocity_x, velocity_y, velocity_z  = self.get_velocity()
        return math.floor(math.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2) * 100.0 * 1.63)


    def update_panels_damage(self, front_left_panel,
                             front_right_panel,
                             rear_left_panel,
                             rear_right_panel,
                             windshield,
                             front_bumper,
                             rear_bumper):
        _, doors, lights, tires = self.get_damage_status()

        panels = encode_panels(front_left_panel,
                               front_right_panel,
                               rear_left_panel,
                               rear_right_panel,
                               windshield,
                               front_bumper,
                               rear_bumper)

        self.set_damage_status(panels, doors, lights, tires)
        self.update_damage()


    def update_doors_damage(self, bonnet, boot, driver_door, passenger_door):
        panels, _, lights, tires = self.get_damage_status()

        doors = encode_doors(bonnet, boot, driver_door, passenger_door)

        self.set_damage_status(panels, doors, lights, tires)
        self.update_damage()


    def update_lights_damage(self, front_left_light, front_right_light, back_lights):
        panels, doors, _, tires = self.get_damage_status()

        lights = encode_lights(front_left_light, front_right_light, back_lights)

        self.set_damage_status(panels, doors, lights, tires)
        self.update_damage()


    def update_tires_damage(self, rear_right_tire, front_right_tire, rear_left_tire, front_left_tire):
        panels, doors, lights, _ = self.get_damage_status()

        tires = encode_tires(rear_right_tire, front_right_tire, rear_left_tire, front_left_tire)

        self.set_damage_status(panels, doors, lights, tires)
        self.update_damage()


    def get_x_y_in_front_of(self, distance: float) -> tuple[float, float]:
        (x, y, z) = self.get_position()
        a = self.get_z_angle()

        x = x + (distance * math.sin(math.radians(-a)))
        y = y + (distance * math.cos(math.radians(-a)))

        return x, y

    # endregion

    # region Registry

    @classmethod
    def from_registry(cls, vehicle: BaseVehicle) -> "Vehicle":
        if isinstance(vehicle, int):
            vehicle_id = vehicle

        if isinstance(vehicle, BaseVehicle):
            vehicle_id = vehicle.id

        vehicle = cls._registry.get(vehicle_id, None)

        if not vehicle:
            cls._registry[vehicle_id] = vehicle = cls(vehicle_id)

        return vehicle

    # endregion


# region STATICS

def decode_panels(panels) -> tuple[int, int, int, int, int, int, int]:
    front_left_panel = panels & 15
    front_right_panel = (panels >> 4) & 15
    rear_left_panel = (panels >> 8) & 15
    rear_right_panel = (panels >> 12) & 15
    windshield = (panels >> 16) & 15
    front_bumper = (panels >> 20) & 15
    rear_bumper = (panels >> 24) & 15
    return front_left_panel, front_right_panel, rear_left_panel, rear_right_panel, windshield, front_bumper, rear_bumper


def encode_panels(front_left_panel, front_right_panel, rear_left_panel, rear_right_panel, windshield, front_bumper,
                  rear_bumper):
    return front_left_panel | (front_right_panel << 4) | (rear_left_panel << 8) | (rear_right_panel << 12) | (
            windshield << 16) | (front_bumper << 20) | (rear_bumper << 24)


# Doors
def decode_doors(doors):
    bonnet = doors & 7
    boot = (doors >> 8) & 7
    driver_door = (doors >> 16) & 7
    passenger_door = (doors >> 24) & 7
    return bonnet, boot, driver_door, passenger_door


def encode_doors(bonnet, boot, driver_door, passenger_door):
    return bonnet | (boot << 8) | (driver_door << 16) | (passenger_door << 24)


# Lights
def decode_lights(lights):
    front_left_light = lights & 1
    front_right_light = (lights >> 2) & 1
    back_lights = (lights >> 6) & 1
    return front_left_light, front_right_light, back_lights


def encode_lights(front_left_light, front_right_light, back_lights):
    return front_left_light | (front_right_light << 2) | (back_lights << 6)


# Tires
def decode_tires(tires):
    rear_right_tire = tires & 1
    front_right_tire = (tires >> 1) & 1
    rear_left_tire = (tires >> 2) & 1
    front_left_tire = (tires >> 3) & 1
    return rear_right_tire, front_right_tire, rear_left_tire, front_left_tire


def encode_tires(rear_right_tire, front_right_tire, rear_left_tire, front_left_tire):
    return rear_right_tire | (front_right_tire << 1) | (rear_left_tire << 2) | (front_left_tire << 3)

# endregion

