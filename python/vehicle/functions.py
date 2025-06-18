import random
import math

from sqlalchemy import select, text

from pysamp import kill_timer, set_timer
from python.database.context_managger import transactional_session
from python.model.database import Vehicle as VehicleDB
from python.model.server import Vehicle, Player
from python.utils.enums.colors import Color
from python.utils.enums.states import State
from python.utils.vars import VEHICLE_PLATE_MAP
from python.server.database import VEHICLE_SESSION


def handle_engine_switch(player: Player, vehicle: Vehicle):
    vehicle: Vehicle = player.get_vehicle()

    if vehicle is None:
        return

    if vehicle.action_lock:
        return

    if vehicle.is_registered:
        if vehicle.is_rentable and vehicle.renter is not None and vehicle.renter.id != player.id:
            return

        if vehicle.is_starting:
            player.send_system_message(Color.RED, "Már indítod!")
            return

        if vehicle.engine:
            player.send_system_message(Color.RED, "Leállítottad a motort!")
            player.make_action("leállította a motort")
            vehicle.engine = 0

            if "engine_run" in vehicle.timers:
                kill_timer(vehicle.timers["engine_run"])
            return

        vehicle.is_starting = True

        if 600.0 <= vehicle.get_health() < 800.0:
            timer_time = 2

        elif 500.0 <= vehicle.get_health() < 600.0:
            timer_time = 5

        elif 400.0 <= vehicle.get_health() < 500.0:
            timer_time = 10

        elif 400.0 >= vehicle.get_health():
            timer_time = 15

        else:
            timer_time = 1

        player.game_text("~w~Indítás...", timer_time * 1000, 3)

        set_timer(do_start_engine, timer_time * 1000, False, (player, vehicle))

    else:
        if vehicle.engine:
            player.send_system_message(Color.RED, "Leállítottad a motort!")
            player.make_action("leállította a motort")
            vehicle.engine = 0

        else:
            player.send_system_message(Color.GREEN, "Elindítottad a motort!")
            player.make_action("elindította a motort")
            vehicle.engine = 1


def do_start_engine(args):

    player: Player = args[0]
    vehicle: Vehicle = args[1]

    health: float = vehicle.get_health()

    can_start: bool = can_start_engine(health) and vehicle.fuel_level > 0.0

    if not can_start and player.get_state() == State.DRIVER:
        player.game_text("~r~Lefulladt", 3000, 3)

        if vehicle.fuel_level == 0:
            player.send_system_message(Color.WHITE, "Nincs üzemanyag a járműben!")

        if 600.0 <= health < 800.0:
            player.send_system_message(Color.WHITE, "Nem ártana elnézni a szervízbe!")

        elif 500.0 <= health < 600.0:
            player.send_system_message(Color.WHITE, "El kellene menni a szervízbe!")

        elif 400.0 <= health < 500.0:
            player.send_system_message(Color.WHITE, "Sűrgősen menj szervízbe!")

        elif 400.0 >= health:
            player.send_system_message(Color.WHITE, "Hívj szerelot, aki megjavítja a jármuvet!")

        vehicle.engine = 0

        if "engine_run" in vehicle.timers:
            kill_timer(vehicle.timers["engine_run"])

    elif can_start and player.get_state() == State.DRIVER:
        player.send_system_message(Color.GREEN, "Elindítottad a motort!")
        player.make_action("elindította a motort")

        vehicle.engine = 1
        vehicle.timers["engine_run"] = set_timer(engine_running_timer, 2500, True, vehicle)

    vehicle.is_starting = False


def can_start_engine(health: float) -> bool:
    if (600.0 < health < 800.0) and random.randint(0, 24) == 12:
        return False

    elif (500.0 < health < 600.0) and random.randint(0, 8) == 4:
        return False

    elif (400.0 < health < 500.0) and random.randint(0, 1) == 1:
        return False

    elif 400.0 > health:
        return False

    return True


def reload_vehicle(db_id: int, in_game_id: int = -1, is_respawn: bool = False) -> None:
    with transactional_session(VEHICLE_SESSION) as session:
        vehicle: VehicleDB | None = session.scalars(select(VehicleDB).where(VehicleDB.id == db_id)).one_or_none()

        if vehicle is None:
            return

        if is_respawn and db_id != -1 and db_id is not None:
            veh = Vehicle.get_registry_item(in_game_id)
            veh.destroy()

            model_id: int = vehicle.vehicle_model_id + 399
            x: float = vehicle.x
            y: float = vehicle.y
            z: float = vehicle.z
            angle: float = vehicle.angle
            color_1: int = vehicle.color_1
            color_2: int = vehicle.color_2

            veh: Vehicle = Vehicle.create(model_id, x, y, z, angle, int(color_1), int(color_2), -1, vehicle.plate)

            vehicle.in_game_id = veh.id
            veh.is_registered = True

            VEHICLE_PLATE_MAP[vehicle.plate] = veh


        elif is_respawn and db_id == -1 and db_id is None:
            veh = Vehicle.get_registry_item(in_game_id)
            veh.destroy()

        elif not is_respawn and in_game_id == -1:
            model_id: int = vehicle.vehicle_model_id + 399
            x: float = vehicle.x
            y: float = vehicle.y
            z: float = vehicle.z
            angle: float = vehicle.angle
            color_1: int = vehicle.color_1
            color_2: int = vehicle.color_2

            veh: Vehicle = Vehicle.create(model_id, x, y, z, angle, int(color_1), int(color_2), -1, vehicle.plate)
            veh.init(int(color_1), int(color_2), vehicle.plate, db_id)

            vehicle.in_game_id = veh.id
            veh.is_registered = True

            VEHICLE_PLATE_MAP[vehicle.plate] = veh

        elif not is_respawn and in_game_id != -1:
            model_id: int = vehicle.vehicle_model_id + 399
            x: float = vehicle.x
            y: float = vehicle.y
            z: float = vehicle.z
            angle: float = vehicle.angle
            color_1: int = vehicle.color_1
            color_2: int = vehicle.color_2

            veh: Vehicle = Vehicle.create(model_id, x, y, z, angle, int(color_1), int(color_2), -1, vehicle.plate)
            veh.init(int(color_1), int(color_2), vehicle.plate, db_id)

            vehicle.in_game_id = veh.id
            veh.is_registered = True

            VEHICLE_PLATE_MAP[vehicle.plate] = veh


def engine_running_timer(vehicle: Vehicle):
    if vehicle.is_registered:
        l_x, l_y, _ = vehicle.last_pos
        x, y, z = vehicle.get_position()
        speed: int = vehicle.get_speed()
        consumption = vehicle.model.consumption
        consumption_multi = consumption * (0.002 if vehicle.fuel_type.code == "B" else 0.01)
        vehicle.last_pos = (x, y, z)

        dist = math.hypot(x - l_x, y - l_y) / 1.0936
        
        if dist > 0:
            vehicle.distance += dist

        if speed > 0:
            fuel_consumption = (vehicle.fuel_level - (((dist / 1000) / 100) * consumption + consumption_multi))
        else:
            fuel_consumption = (vehicle.fuel_level - (consumption / 360 * (2.5 / 3600) + consumption_multi))

        if vehicle.job_id is not None:
            vehicle.fuel_level = fuel_consumption

            if vehicle.fuel_level <= 0.0:
                vehicle.fuel_level = 0

            if "engine_run" in vehicle.timers:
                kill_timer(vehicle.timers["engine_run"])
            vehicle.engine = 0


def player_in_car_handler(player: Player, vehicle: Vehicle):
    if player.get_state() == State.DRIVER:    
        applay_limiter(player, vehicle)
            
        speed = vehicle.get_speed()
        player.update_speedo_speed(speed)
        player.update_speedo_dist(int(vehicle.distance / 1000))

        if vehicle.is_registered and vehicle.fuel_type:
            player.update_speedo_fuel_type(vehicle.fuel_type.code)

        else:
            player.update_speedo_fuel_type("N")

        if vehicle.engine == 1:
            if vehicle.is_registered:
                fuel_prec = int(vehicle.fuel_level / vehicle.model.tank_capacity * 10)
                fuel_prec = fuel_prec if fuel_prec > 0 else 1
                player.update_speedo_fuel_level(fuel_prec)

            if speed == 0:
                player.update_speedo_trans("~w~R ~p~N ~w~D")

            elif not vehicle.is_driving_backwards():
                player.update_speedo_trans("~w~R ~p~N ~w~D") if speed < 1 else player.update_speedo_trans("~w~R N ~p~D")

            elif vehicle.is_driving_backwards():
                player.update_speedo_trans("~p~R ~w~N D")

        else:
            player.update_speedo_fuel_level(1)


        if vehicle.fix_veh or vehicle.skip_check_damage:
            vehicle.skip_check_damage = False

        elif player.get_state() == State.DRIVER and vehicle.get_health() != vehicle.health:

            if (damage := round(float(vehicle.health) - vehicle.get_health(), 0)) > 0:
                on_vehicle_damage(vehicle, damage)

            vehicle.health = vehicle.get_health()

            if vehicle.is_registered:
                vehicle.update_damage()


def on_vehicle_damage(vehicle: Vehicle, damage: float):
    if damage % 5 == 0 or vehicle.skip_check_damage:
        return

    vehicle.skip_check_damage = True

    match vehicle.get_model():
        case 543 | 605:
            damage *= 1.95

        case 448 | 461 | 462 | 463 | 468 | 481 | 471 | 509 | 510 | 521 | 522 | 523 | 581 | 586:
            damage *= 2.95

        case 528:
            damage *= .35

    need_remove_players: list[Player] = []

    for passenger in vehicle.passengers:
        if damage < 45:
            break

        passenger_veh = passenger.get_vehicle()

        if passenger_veh is None or passenger_veh.id != vehicle.id:
            need_remove_players.append(passenger)
            continue

        msg: str
        action: str
        lvl: float = 2000

        if 45 <= damage <= 69:
            msg = "Könnyeben megsérültél!"
            action = "könnyeben megsérült"
            lvl += int((damage / 3) * 100)

        elif 70 <= damage <= 109:
            msg = "Súlyosan megsérültél!"
            action = "súlyosan megsérült"
            lvl += int(2000 + (damage / 3) * 100)

        elif 110 <= damage <= 179:
            msg = "Életveszélyesen megsérültél!"
            action = "életveszélyesen megsérült"
            lvl += int(4000 + (damage / 3) * 100)

        else:
            msg = "Szörnyethaltál autóbalesetben"
            action = "Szörnyethalt autóbalesetben"
            lvl = 0

        passenger.send_system_message(Color.RED, msg)
        passenger.make_action(action)
        passenger.set_drunk_level(lvl)

    for player in need_remove_players:
        vehicle.remove_passenger(player)


def applay_limiter(player: Player, vehicle: Vehicle):
    if not vehicle.limiter:
        return
    
    s_cap = vehicle.limiter
    if s_cap == 0:
        return

    s_fX, s_fY, s_fZ = vehicle.get_position()
    s_fVX, s_fVY, s_fVZ = vehicle.get_velocity()
                       
    if  not player.is_in_range_of_point(s_cap + 0.05, s_fX + s_fVX, s_fY + s_fVY, s_fZ + s_fVZ):
        s_fLength = math.sqrt( ( s_fVX * s_fVX ) + ( s_fVY * s_fVY ) + ( s_fVZ * s_fVZ ) )

        s_fVX = ( s_fVX / s_fLength ) * s_cap
        s_fVY = ( s_fVY / s_fLength ) * s_cap
        s_fVZ = ( s_fVZ / s_fLength ) * s_cap
        vehicle.set_velocity(s_fVX, s_fVY, s_fVZ )
