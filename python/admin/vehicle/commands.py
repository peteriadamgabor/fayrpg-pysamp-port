import random
import string

from pysamp import kill_timer, set_timer
from python.utils.helper.python import try_parse_int
from sqlalchemy import select

from pyeSelect.eselect import Menu, MenuItem
from python.database.context_managger import transactional_session
from python.model.database import Vehicle as VehicleDB
from python.model.database import FuelType as FuelTypeDB
from python.model.database import VehicleModel as VehicleModelDB
from python.model.dto import VehicleModel as VehicleModelDTO
from python.model.server import Player, Vehicle
from python.server.database import VEHICLE_SESSION
from python.utils.enums.colors import Color
from python.utils.enums.translation_keys import TranslationKeys
from python.utils.globals import MIN_VEHICLE_MODEL_ID, MAX_VEHICLE_MODEL_ID
from python.utils.vars import VEHICLE_PLATE_MAP
from python.vehicle.functions import reload_vehicle
from ..functions import check_player_role_permission, spawn_admin_car
from python.model.transorm import Transform

@Player.command(args_name=("modelid/modelname", "color1", "color2"), requires=[check_player_role_permission])
@Player.using_registry
def newcar(player: Player, model_id: str | int, color1: int = 1, color2: int = 0):
    if model_id.isdigit() and (int(model_id) > MAX_VEHICLE_MODEL_ID or MIN_VEHICLE_MODEL_ID > int(model_id)):
        player.send_client_message(Color.RED, "(( Hiba: nincs ilyen model! ))")
        return

    if not model_id.isdigit():
        model_id = Vehicle.get_model_id_by_name(model_id)

    if model_id is None:
        player.send_client_message(Color.RED, "(( Hiba: Nincs ilyen típusú jármu! ))")
        return

    model_id = int(model_id)

    if model_id == 520 or model_id == 425 or model_id == 538 or model_id == 570 or model_id == 569 or model_id == 537:
        player.send_client_message(Color.RED, "(( Hiba: Ezt a jármuvet nem használhatod! ))")
        return

    (_, _, z) = player.get_pos()
    angle: float = player.get_facing_angle() + 90 if player.get_facing_angle() < 0 else player.get_facing_angle() - 90
    x, y = player.get_x_y_in_front_of(5)

    plate: str = "NINCS"
    Vehicle.create(model_id, x, y, z, angle, int(color1), int(color2), -1, plate)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def newcarl(player: Player, color1: int = 1, color2: int = 0):
    forbidden = [520, 425, 538, 570, 569, 537]

    menu = Menu(
        'Autók',
        [MenuItem(i, '', -15.0, 0.0, -45.0, 1, int(color1), int(color2)) for i in range(400, 612) if
         i not in forbidden],
        on_select=spawn_admin_car,
    )

    menu.show(player)

@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def showcarcolor(player: Player, model_id: str | int):

    if model_id.isdigit() and (int(model_id) > MAX_VEHICLE_MODEL_ID or MIN_VEHICLE_MODEL_ID > int(model_id)):
        player.send_client_message(Color.RED, "(( Hiba: nincs ilyen model! ))")
        return

    if not model_id.isdigit():
        model_id = Vehicle.get_model_id_by_name(model_id)

    if model_id is None:
        player.send_client_message(Color.RED, "(( Hiba: Nincs ilyen típusú jármu! ))")
        return

    model_id = int(model_id)


    if model_id == 520 or model_id == 425 or model_id == 538 or model_id == 570 or model_id == 569 or model_id == 537:
        player.send_client_message(Color.RED, "(( Hiba: Ezt a jármuvet nem használhatod! ))")
        return

    model: VehicleModelDTO = Transform.get_dto(VehicleModelDB, VehicleModelDTO, model_id - 399)

    if model.color_number == 1:
        menu = Menu(
            model.name,
            [MenuItem(model_id, f'({i}, {1})', -15.0, 0.0, -45.0, 1, int(i), int(1)) for i in range(256)],
            on_select=spawn_admin_car,
        )

    else:
        items = []
        for i in range(256):
            for j in range(256):
                items.append(MenuItem(model_id, f'({i}, {j})', -15.0, 0.0, -45.0, 1, i, j))

        menu = Menu(model.name, items, on_select=spawn_admin_car,)

    menu.show(player)


@Player.command(args_name=("Kocsi DBID",), requires=[check_player_role_permission])
@Player.using_registry
def oldplayer(player: Player, vehicle_id: int = -1):
    vehicle: Vehicle | None = None

    if vehicle_id == -1:
        vehicle = player.get_vehicle()
    else:
        vehicle = Vehicle.get_registry_item(vehicle_id)

    if not vehicle:
        player.send_client_message(Color.RED, "(( Nincs ilyen jármű ))")
        return

    player.send_client_message(-1, "(( Kocsiban ült játéksok: ))")
    for row in vehicle.get_passenger_activity():
        player.send_client_message(-1, f"(( {row} ))")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def fixveh(player: Player):
    vehicle: Vehicle = player.get_vehicle()

    if vehicle:
        vehicle.fix_veh = True

        player.send_system_message_multi_lang(Color.GREEN, TranslationKeys.FIXVEH)
        vehicle.health = 1_000
        vehicle.repair()

        set_timer(vehicle.set_fix_veh, 1000, False, False)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def setvehhp(player: Player, health: float):
    vehicle: Vehicle = player.get_vehicle()

    if vehicle:
        vehicle.skip_check_damage = True
        vehicle.health = health


@Player.command(args_name=("id/név",), requires=[check_player_role_permission])
@Player.using_registry
def savecar(player: Player):
    if not player.is_in_any_vehicle():
        player.send_system_message(Color.RED, "Nem ülsz járműben!")
        return

    if player.in_vehicle():
        player.send_system_message(Color.RED, "Ez a járműben már szerepel a rendszerben!")
        return

    veh: Vehicle = player.get_vehicle()
    model_id: int = veh.get_model()
    x, y, z = veh.get_position()
    a = veh.get_z_angle()
    color_1, color_2 = veh.color_1, veh.color_2

    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=3))
    plate = f"{letters}-{numbers}"
    veh.destroy()

    with transactional_session(VEHICLE_SESSION) as session:

        fuel_type: FuelTypeDB = session.scalars(select(FuelTypeDB).where(FuelTypeDB.code == "B")).one()
        veh_model: VehicleModelDB = session.scalars(select(VehicleModelDB).where(VehicleModelDB.id == (model_id-399))).one()


        new_vehicle_data = VehicleDB(
            in_game_id=None,
            vehicle_model_id=veh_model.id,
            x=x,
            y=y,
            z=z,
            angle=a,
            color_1=color_1,
            color_2=color_2,
            plate=plate,
            fuel_type_id = fuel_type.id,
            fill_type_id = fuel_type.id,
            fuel_level = veh_model.tank_capacity
        )
        session.add(new_vehicle_data)

    with transactional_session(VEHICLE_SESSION) as session:
        car = session.scalars(select(VehicleDB).order_by(VehicleDB.id.desc())).first() 
        veh: Vehicle = Vehicle.create(model_id, x, y, z, a, int(color_1), int(color_2), -1, car.plate)
        car.in_game_id = veh.id
        VEHICLE_PLATE_MAP.setdefault(car.plate, veh)

    player.send_system_message(Color.GREEN, "Jármű sikeresen elmentve!")
    player.send_system_message(Color.GREEN, f"Forgalmi rendszám: {plate}")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def respawncar(player: Player, car_id: int = -1):
    vehicle: Vehicle

    if car_id == -1:
        vehicle = player.get_nearest_vehicle(7.0)
    else:
        vehicle = Vehicle.get_registry_item(car_id)

    if vehicle is None:
        player.send_system_message(Color.ORANGE, "Nincs jármű a közelben!" if car_id == -1 else "Nincs ilyen jármű!")
        return

    player.send_system_message(Color.GREEN, "Jármű respawnolva!")

    reload_vehicle(vehicle.dbid, vehicle.id, True)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def rnc(player: Player):
    player.send_system_message(Color.GREEN, "Járművek respawnolva!")

    for i in Vehicle.get_registry_items():
        if i is not None:
            if player.get_distance_from_point(i.get_position()) <= 50:
                reload_vehicle(i.dbid, i.id, True)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def carid(player: Player, car_id: int = -1):
    vehicle: Vehicle = None

    if car_id == -1:
        vehicle = player.get_vehicle()
    else:
        vehicle = Vehicle.get_registry_item(car_id)

    if vehicle is None:
        player.send_system_message(Color.ORANGE, "Nem ülsz járműben!" if car_id == -1 else "Nincs ilyen jármű!")
        return

    if vehicle.is_registered:
        player.send_system_message(Color.GREEN, f"DBID: {vehicle.db_id} | ID: {vehicle.id} | Rendszám: {vehicle.plate} ")

        if vehicle.owner:
            player.send_system_message(Color.GREEN,
                                       f"Tulajdonos: {vehicle.owner.name.replace('_', ' ')}[{vehicle.owner.id}] ")
    else:
        player.send_system_message(Color.GREEN, f"DBID: NINCS | ID: {vehicle.id} | Rendszám: NINCS ")

    player.send_system_message(Color.GREEN, f"Szín(ek): ({vehicle.color_1}, {vehicle.color_2}) | Bérelhető: {"Igen" if vehicle.is_rentable else "Nem"}")

    if vehicle.is_rentable:
        if vehicle.rent_started:
            rent_start_str = f"{vehicle.rent_started:%Y.%m.%d %X}"
        else:
            rent_start_str = "-"

        if vehicle.rent_started:
            rent_end_str = f"{vehicle.rent_end:%Y.%m.%d %X}"
        else:
            rent_end_str = "-"

        player.send_system_message(Color.GREEN, f"Bérlés kezdete: {rent_start_str} | Bérlés vége: {rent_end_str}")
        player.send_system_message(Color.GREEN, f"Bérlő: {vehicle.renter.name if vehicle.renter else "Nincs"}")




@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def gotocar(player: Player, car_id: int, passenger: int = -1):
    vehicle: Vehicle = Vehicle.get_registry_item(int(car_id))

    if vehicle is None:
        player.send_system_message(Color.ORANGE, "Nincs ilyen jármű!")
        return

    if (passenger := try_parse_int(passenger)) is None:
        player.send_system_message(Color.ORANGE, "Számmal kell megadni!")
        return
    
    if passenger > -1:
        player.put_in_vehicle(vehicle.id,passenger)
    else:
        player.set_pos(*vehicle.get_position())
        player.send_system_message(Color.GREEN, f"A járműhöz lettél telportálva!")
        player.interior = 0
        player.virtual_world = 0

@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def getcar(player: Player, car_id: int):
    vehicle: Vehicle = Vehicle.get_registry_item(int(car_id))

    if vehicle is None:
        player.send_system_message(Color.ORANGE, "Nincs ilyen jármű!")
        return

    _, _, z = player.get_pos()
    x, y = player.get_x_y_in_front_of(5)

    vehicle.set_position(x, y, z + 2)
    player.send_system_message(Color.GREEN, f"Itt a járműved!")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def ai(player: Player):
    vehicle: Vehicle = player.get_vehicle()

    if vehicle is None:
        player.send_system_message(Color.ORANGE, "Nem ülsz járműben!")
        return

    if "engine_run" in vehicle.timers:
        kill_timer(vehicle.timers["engine_run"])

    vehicle.engine = 1

@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def lefoglal(player: Player):
    vehicle: Vehicle | None = player.get_nearest_vehicle(7.0)

    if vehicle is None or player.in_vehicle():
        return

    player.put_in_vehicle(vehicle.id, 0)
    
    if "engine_run" in vehicle.timers:
            kill_timer(vehicle.timers["engine_run"])

    vehicle.engine = 1


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def fuelcar(player: Player):
    vehicle: Vehicle = player.get_vehicle()

    if vehicle is None:
        player.send_system_message(Color.ORANGE, "Nem ülsz járműben!")
        return

    vehicle.fuel_level = vehicle.model.tank_capacity
    player.send_system_message(Color.ORANGE, "Jármű megtankolva!")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def maptele(player: Player, allapot: str):
    
    if allapot == "be":        
        if "maptele" in player.custom_vars:
            player.send_system_message(Color.ORANGE, "Map Teleport már be van kapcsolva!")
        else:
            player.custom_vars["maptele"] = True
            player.send_system_message(Color.GREEN, "Map Teleport bekapcsolva!")
        return
    elif allapot == "ki":
        if "maptele" in player.custom_vars:
            del player.custom_vars["maptele"]
            player.send_system_message(Color.GREEN, "Map Teleport kikapcsolva!")
        else:
            player.send_system_message(Color.ORANGE, "Map Teleport már ki van kapcsolva!")
        return
    else:
        player.send_system_message(Color.GREEN, "/maptele [be/ki]")
        return
