import importlib
import random
from types import NoneType

from pysamp import set_timer, kill_timer
from pysamp.playerobject import PlayerObject
from pystreamer.dynamicobject import DynamicObject
from python.model.database import teleport
from python.model.server import Player, Vehicle as VehicleSRV
from python.server.database import MAIN_SESSION
from python.utils.enums.colors import Color
from python.utils.helper.python import try_parse_int
from ..functions import check_player_role_permission, add_record_rout_point
from ... import exception_logger


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
@exception_logger.catch
def recordrout(player: Player, rout_name: str = "ROUT_NAME", freq: int = 5):
    if "recorded_rout_name" not in player.custom_vars:
        player.send_system_message(Color.GREEN, f"Útvonal felvétel elkezdődött! {freq} mp ként ment egy pontot!")

        pos = player.get_pos()

        player.custom_vars["recorded_rout_name"] = rout_name
        player.custom_vars["recorded_rout_points"] = [pos]
        player.set_checkpoint(pos[0], pos[1], pos[2], 5)

        player.timers["recorded_rout_timer"] = set_timer(add_record_rout_point, int(freq) * 1000, True, player)

    else:
        player.send_system_message(Color.GREEN,
                                   f"Útvonal felvétel mentve {player.custom_vars["recorded_rout_name"]} néven!")
        kill_timer(player.timers["recorded_rout_timer"])
        f_name = player.custom_vars["recorded_rout_name"]

        with open(f"scriptfiles/routs/records/{f_name}.json", "w+") as f:
            string_buffer = []

            for item in player.custom_vars["recorded_rout_points"]:
                string_buffer.append(
                    "{" + '"x":' + str(item[0]) + ', "y":' + str(item[1]) + ', "z":' + str(item[2]) + "}")

            j_string = ", ".join(string_buffer)
            f.write("[" + j_string + "]")

        del player.custom_vars["recorded_rout_name"]
        del player.custom_vars["recorded_rout_points"]
        del player.timers["recorded_rout_timer"]


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def debug(player: Player, debug_type: str, *args):
    player.send_system_message(Color.WHITE, "|--------------[DEBUG INFO]--------------|")
    match debug_type:
        case "veh":
            for i in VehicleSRV.get_registry_items():
                player.send_system_message(Color.WHITE, f"ig id: {i.id} | db id: {i.dbid} | colors: ({i.color_1}, {i.color_2}) | plate: {i.plate}")
                player.send_system_message(Color.WHITE, f"dist: {i.get_distance_from_point(*player.get_pos())} ")

        case "wep":
            for i in range(13):
                weapon, ammo = player.get_weapon_data(i)
                player.send_system_message(Color.WHITE, f"Weapon ID: {weapon} || Ammo: {ammo}")

        case "lv":
            vehicles: list[VehicleSRV] = player.get_nearest_vehicles()
            for i in vehicles:
                player.send_system_message(Color.WHITE, f"ig id: {i.id} | db id: {i.dbid} | colors: ({i.color_1}, {i.color_2}) | plate: {i.plate}")
                player.send_system_message(Color.WHITE, f"dist: {i.get_distance_from_point(*player.get_pos())} ")

        case "p":
            x,y,z = player.get_pos()
            player.send_system_message(Color.WHITE, f"Name: {player.name} || HP: {player.get_health()} || Armour: {player.get_armour()}")
            player.send_system_message(Color.WHITE, f"X: {x} || Y: {y} || Z: {z} ")
            player.send_system_message(Color.WHITE, f"Interior: {player.interior} || VirtualWord : {player.virtual_world}")

        case _:
            player.send_system_message(Color.WHITE, "Types: p, veh, wep, lv, chr")

    player.send_system_message(Color.WHITE, "|--------------[DEBUG INFO]--------------|")

@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def dn(player: Player):
    x, y, z = player.get_pos()
    player.set_pos(x, y, z - 5)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def up(player: Player):
    x, y, z = player.get_pos()
    player.set_pos(x, y, z + 5)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def mark(player: Player, id: int = -1):
    if (marker_id := try_parse_int(id)) is None:
        player.send_system_message(Color.WHITE, f"Számmal kell megadni!")

    if id != -1:
        player.markers[marker_id] = (player.get_pos(), player.get_interior(), player.get_virtual_world())

    else:
        player.markers[0] = (player.get_pos(), player.get_interior(), player.get_virtual_world())


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def gotomark(player: Player, id: int = -1):
    if (marker_id := try_parse_int(id)) is None:
        return

    mark_pos = player.markers[marker_id] if id != -1 else player.markers[0]

    if mark_pos is None:
        return

    else:
        player.set_back_pos()

        player.set_pos(*mark_pos[0])
        player.set_interior(mark_pos[1])
        player.set_virtual_world(mark_pos[2])


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def listmarks(player: Player):
    for i, e in enumerate(player.markers):
        if e is not None:
            player.send_system_message(Color.WHITE, f"{i} - {e}")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def createteleport(player: Player, name: str):
    if "teleport1" not in player.custom_vars:
        player.custom_vars["teleport1"] = [player.get_pos(), player.get_interior(), player.get_virtual_world()]
        player.send_system_message(Color.GREEN, "Egyes pont elmentve. Menny a kövi pontra!")
    else:
        with MAIN_SESSION() as session:
            x, y, z = player.get_pos()
            interior = player.get_interior()
            vw = player.get_virtual_world()
            a = player.get_facing_angle()

            tp = teleport(from_x=player.custom_vars["teleport1"][0][0],
                          from_y=player.custom_vars["teleport1"][0][1],
                          from_z=player.custom_vars["teleport1"][0][2],
                          from_interior=player.custom_vars["teleport1"][1],
                          from_vw=player.custom_vars["teleport1"][2],
                          radius=5.0,
                          to_x=x,
                          to_y=y,
                          to_z=z,
                          to_angel=a,
                          to_interior=interior,
                          to_vw=vw,
                          description=name)

            session.add(tp)
            session.commit()
            del player.custom_vars["teleport1"]
            player.send_system_message(Color.GREEN, "Sikeresen elmentetted a teleportot!")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def reloadteleports(player: Player):
    player.send_system_message(Color.JB_RED, "MEG KELL ÍRNI")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def fly(player: Player):
    if "fly_mode" in player.custom_vars:
        obj: PlayerObject = player.custom_vars["fly_mode"]["object"]

        player.send_system_message(Color.GREEN, "Repülés kikapcsolva!")
        player.toggle_spectating(False)
        player.cancel_edit()
        player.set_back_pos(given_pos=obj.get_position(), given_interior=player.interior, given_vw=player.virtual_world)

        obj.destroy()
        del player.custom_vars["fly_mode"]

    else:
        x, y, z = player.get_pos()
        obj: PlayerObject = PlayerObject.create(player, 19300, x, y, z, 0.0, 0.0, 0.0, 0.0)
        player.toggle_spectating(True)
        player.attach_camera_to_player_object(obj)

        player.custom_vars["fly_mode"] = {"object": obj, "mode": 0, "last_move": 0, "keys": 0, "ud": 0, "lr": 0,
                                          "accelmul": 0.0}
        player.send_system_message(Color.GREEN, "Repülés bekapcsolva!")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def minetest(player: Player, n: int, m: int):
    x, y, z = player.get_pos()

    matrix = []

    for _ in range(int(n)):
        n_list = []
        for _ in range(int(m)):
            obj = DynamicObject.create(19551, x, y, z, 0.0, 0.0, 0.0)

            rng = random.randint(0, 5)

            if rng == 2:
                _ = DynamicObject.create(19943, x, y, z, 0.0, 0.0, 0.0)

            if rng == 3:
                _ = DynamicObject.create(2030, x, y, z, 0.0, 0.0, 0.0)

            n_list.append(obj)
            y += 125.0
        x += 125
        y = (y - (125 * int(m)))
        matrix.append(n_list)
