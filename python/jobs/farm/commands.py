import json
import os
import random

from pysamp import attach_trailer_to_vehicle
from python.model.server import Player, Vehicle
from python.logging.loggers import exception_logger
from python.utils.enums.colors import Color
from python.utils.helper.python import format_numbers


@Player.command
@Player.using_registry
@exception_logger.catch
def tanya(player: Player, action: str = ""):
    if action == "":
        player.send_system_message(Color.WHITE, "Használat: /tanya [tipus]")
        player.send_system_message(Color.WHITE, "Típusok: potkocsi, mag, felpakol, elad")
        return

    if action.lower() == "potkocsi":
        if not player.in_vehicle(531) and not player.in_vehicle(478):
            player.send_system_message(Color.ORANGE, "Nem ülsz megfelelő járműben")
            return

        player_veh: Vehicle = player.get_vehicle()

        if player_veh.is_trailer_attached():
            player_veh.detach_trailer()
            return

        farm_veh_1: Vehicle = player.get_nearest_vehicle(10.0, 610)
        farm_veh_2: Vehicle = player.get_nearest_vehicle(10.0, 611)

        if farm_veh_1 is None and farm_veh_2 is None:
            player.send_system_message(Color.ORANGE, "Nincs a közeledben pótkocsi!")
            return

        attach_trailer_to_vehicle(farm_veh_1.id if farm_veh_1 is not None else farm_veh_2.id, player_veh.id)
        return

    elif action.lower() == "mag":
        path_base = "scriptfiles/routs/jobs/sweeper/M"
        pay_ment = random.randint(6_500, 12_000)

    elif action.lower() == "felpakol":
        path_base = "scriptfiles/routs/jobs/sweeper/L"
        pay_ment = random.randint(12_000, 15_000)

    elif action.lower() == "elad":
        path_base = "scriptfiles/routs/jobs/sweeper/L"
        pay_ment = random.randint(12_000, 15_000)

    else:
        player.send_system_message(Color.RED, "Hibás típus!")
        player.send_system_message(Color.WHITE, "Típusok: potkocsi, mag, felpakol, elad")
        return

    files = os.listdir(path_base)
    files = [file for file in files if os.path.isfile(os.path.join(path_base, file))]

    if not files:
        player.send_system_message(Color.RED, "Most nincs ilyen útvonal!")
        return

    random_file = random.choice(files)
    with open(os.path.join(path_base, random_file), "r") as f:
        player.custom_vars["sweeper_pos"] = json.load(f)

    player.custom_vars["sweeper_job"] = 0
    player.custom_vars["sweeper_pay"] = pay_ment

    pos_json = player.custom_vars["sweeper_pos"][0]
    player.set_checkpoint(pos_json["x"], pos_json["y"], pos_json["z"], size=5)

    player.send_system_message(Color.GREEN, "Elkezted a mukát!")
    player.send_system_message(Color.GREEN, "Kövesd a piros check pointokat!")
    player.send_system_message(Color.GREEN,
                               f"A munka végén {format_numbers(pay_ment)} Ft fog jóváíródni a fizetésedhez!")
