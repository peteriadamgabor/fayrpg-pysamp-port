import json
import random

from python.model.server import Player
from python.logging.loggers import exception_logger
from python.utils.enums.colors import Color
from python.utils.helper.python import format_numbers, get_a_random_file
from config import settings

@Player.command
@Player.using_registry
@exception_logger.catch
def uttisztito(player: Player, rout_type: str = ""):

    if not player.in_vehicle(574):
        player.send_system_message(Color.ORANGE, "Nem ülsz a megfelelő járműben!")
        return

    if "sweeper_job" in player.custom_vars:
        player.send_system_message(Color.ORANGE, "Nem ülsz a megfelelő járműben!")
        return

    if rout_type == "":
        player.send_system_message(Color.WHITE, "Használat: /uttisztito [tipus]")
        player.send_system_message(Color.WHITE, "Típusok: rövid, közepes, hosszú")
        return

    if rout_type.lower() == "rövid" or rout_type.lower() == "rovid":
        path_base = settings.paths.SWEEPTER_ROUTS + "/S"
        pay_ment = random.randint(1_000, 6_500)

    elif rout_type.lower() == "közepes" or rout_type.lower() == "kozepes":
        path_base = settings.paths.SWEEPTER_ROUTS + "/M"
        pay_ment = random.randint(6_500, 12_000)

    elif rout_type.lower() == "hosszú" or rout_type.lower() == "hosszu":
        path_base = settings.paths.SWEEPTER_ROUTS + "/L"
        pay_ment = random.randint(12_000, 15_000)

    else:
        player.send_system_message(Color.RED, "Hibás típus!")
        player.send_system_message(Color.WHITE, "Típusok: rövid, közepes, hosszú")
        return

    with open(get_a_random_file(path_base), "r") as f:
        player.custom_vars["sweeper_pos"] = json.load(f)

    player.custom_vars["sweeper_job"] = 0
    player.custom_vars["sweeper_pay"] = pay_ment

    pos_json = player.custom_vars["sweeper_pos"][0]
    player.set_checkpoint(pos_json["x"], pos_json["y"], pos_json["z"], size=5)

    player.send_system_message(Color.GREEN, "Elkezted a mukát!")
    player.send_system_message(Color.GREEN, "Kövesd a piros check pointokat!")
    player.send_system_message(Color.GREEN,
                               f"A munka végén {format_numbers(pay_ment)} Ft fog jóváíródni a fizetésedhez!")
