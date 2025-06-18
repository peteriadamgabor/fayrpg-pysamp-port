import json
import random

from pysamp.dialog import Dialog
from python.model.server import Player
from python.logging.loggers import exception_logger
from python.utils.enums.colors import Color
from python.utils.enums.dialog_style import DialogStyle
from python.utils.helper.python import load_all_files, round_to_nearest_hundred
from python.utils.enums.states import State
from python.model.server import Vehicle
from pysamp import set_timer

from config import settings

@Player.command
@Player.using_registry
@exception_logger.catch
def kikoto(player: Player, functione: str = ""):

    if functione == "":
        player.send_system_message(Color.WHITE, "Használat: /kikoto [tipus]")
        player.send_system_message(Color.WHITE, "Típusok: tachograf(tchm), berakod, kirakod, munkaruha, lista") #hello szia
        return
    
    if not player.in_vehicle(484) and not player.in_vehicle(453):
        player.send_system_message(Color.ORANGE, "Nem ülsz a megfelelő járműben!")
        return

    if "in_job" in player.custom_vars:
        player.send_system_message(Color.ORANGE, "Már dolgozol!")
        return

    if player.get_state() != State.DRIVER:
        player.send_system_message(Color.ORANGE, "Nem te vagy a sofőr!")
        return
    
    vehicle: Vehicle = player.get_vehicle()

    if vehicle.action_lock:
        player.send_system_message(Color.ORANGE, "Éppen dolgoznak a hajón!")
        return
    
    if vehicle.engine:
        player.send_system_message(Color.ORANGE, "Előbb állísd le a motort!")
        return

    points = load_all_files(settings.paths.HARBOUR_POINTS)
    actual_point = None

    for index, point in enumerate(points):
        if player.is_in_range_of_point(point["r"], point["x"], point["y"], point["z"]):
            actual_point = point
            del points[index]
            break

    if functione.lower() == "berakod":

        if not actual_point:
            player.send_system_message(Color.ORANGE, "Nem állsz egy kikötőben sem!")
            return
        if vehicle.is_loaded:
            player.send_system_message(Color.ORANGE, "Már meg van pakolva!")
            return
        if player.get_skin() != 292:
            player.send_system_message(Color.ORANGE, "Nem vagy munkaruhában!")
            return

        rng_point = random.choice(points)
        player.custom_vars["port"] = rng_point
        player.custom_vars["start_port"] = actual_point

        vehicle.action_lock = True
        vehicle.is_loaded = True
        player.toggle_controllable(False)
        rndint = random.randint(5,30)*1000
        player.game_text("~w~Töltés folyamtban", rndint, 3)

        set_timer(player.toggle_controllable, rndint, False, True)
        set_timer(vehicle.set_action_lock, rndint, False, False)
        set_timer(player.set_checkpoint,rndint, False, rng_point["x"], rng_point["y"], rng_point["z"], rng_point["r"])
        set_timer(player.send_system_message, rndint, False, Color.GREEN, "Berakodás befejezve! \nKikötő jelölve a térképen!")

    elif functione.lower() == "kirakod":
        if "port" not in player.custom_vars and player.is_in_range_of_point(player.custom_vars["port"]["r"], player.custom_vars["port"]["x"], player.custom_vars["port"]["y"], player.custom_vars["port"]["z"]):
            player.send_system_message(Color.ORANGE, "Nem vagy a megfelelő kikötőben!")
            return
        
        if not vehicle.is_loaded:
            player.send_system_message(Color.ORANGE, "Nincs megpakolva!")
            return
        
        if player.get_skin() != 292:
            player.send_system_message(Color.ORANGE, "Nem vagy munkaruhában!")
            return
        
        vehicle.action_lock = True
        vehicle.is_loaded = False
        player.toggle_controllable(False)
        rndint = random.randint(5,30)*1000
        player.game_text("~w~Kirakodás folyamtban", rndint, 3)

        distance = player.distance_from_point(player.custom_vars["start_port"]["x"],player.custom_vars["start_port"]["y"],player.custom_vars["start_port"]["z"]) * 0.9144
        distance = (distance/1000)*5*1.5*0.539
        priceperkm = 0

        if player.in_vehicle(484):
            priceperkm = 1125+(35*random.randint(400,4000)/1000)
        else:
            priceperkm = 1140+(70*random.randint(400,2000)/1000)

        price = round_to_nearest_hundred(priceperkm*distance)

        set_timer(player.toggle_controllable, rndint, False, True)
        set_timer(vehicle.set_action_lock, rndint, False, False)
        set_timer(player.send_system_message, rndint, False, Color.GREEN, f"Kirakodás befejezve!")
        set_timer(player.add_payment, rndint, False, price)
        
        del player.custom_vars["port"]
        del player.custom_vars["start_port"]
        
    
    elif functione.lower() == "munkaruha":
        if player.get_skin() != 292:
            player.send_system_message(Color.GREEN, "Felvetted a munkaruhát!")
            player.set_skin(292)
        else:
            player.send_system_message(Color.GREEN, "Levetedd a munkaruhát!")
            player.set_skin(player.skin.id)

    elif functione.lower() == "lista":
        dialog = Dialog.create(DialogStyle.LIST,"Kikötők", "\n".join([i["name"] for i in load_all_files(settings.paths.HARBOUR_POINTS)]), "Kiválaszta", "Bezár", handel_port_list)
        player.show_dialog(dialog)

    else:
        player.send_system_message(Color.RED, "Hibás típus!")
        player.send_system_message(Color.WHITE, "Típusok: tachograf(tchm), berakod, fuvar, kirakod, munkaruha")
        return


def handel_port_list(player: Player, response: int, listitem: int, input_text: str):
    if not bool(response):
        return

    for i in load_all_files(settings.paths.HARBOUR_POINTS):
        if i["name"] == input_text: 
            player.set_checkpoint(i["x"], i["y"], i["z"], 15.0)
            break
