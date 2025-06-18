import datetime
import random

from pysamp.dialog import Dialog
from python.model.server import Player
from python.logging.loggers import exception_logger
from python.utils.enums.colors import Color
from python.utils.enums.dialog_style import DialogStyle
from python.model.server import Vehicle
from pysamp import kill_timer, set_timer
from python.utils.enums.jobs import JobsTypeEnum

@Player.command
@Player.using_registry
@exception_logger.catch
def halasz(player: Player, functione: str = "", *args):

    if functione == "":
        player.send_system_message(Color.WHITE, "Használat: /halasz [tipus]")
        player.send_system_message(Color.WHITE, "Típusok:  etetoanyag, leenged, behuz, tartalom, kirakod")
        return

    if player.job != JobsTypeEnum.FISHERMAN:
        player.send_system_message(Color.ORANGE, "Nem vagy halász!")
        return
    
    if player.is_in_any_vehicle():
        player.send_system_message(Color.ORANGE, "Volán mögül nem használhatod!")
        return
    
    
    if not player.get_nearest_vehicle(5,453):
        player.send_system_message(Color.ORANGE, "Nem vagy halászhajón!")
        return
    vehicle : Vehicle = player.get_nearest_vehicle(5,453)

    if player.in_duty:
        player.send_system_message(Color.ORANGE, "Szolgálatban nem lehet!")
        return        
    
    if functione in ["etetoanyag","etetőanyag"]:
        if player.is_in_ashlar(-3359.9314, -2923.1167, -10, 3120.1536, 3026.4646, 10):
            player.send_system_message(Color.ORANGE, "Menj ki a nyílt vízre!")
            return
        
        if "fishingnet_in" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "A halászháló le van engedve!")
            return
        
        if len(args) == 0:
            player.send_system_message(Color.ORANGE, "Ismeretlen csali!\nCsali típusok: a, b, c")
            return
        
        if args[0] == "a":
            vehicle.custom_vars["fisherman_feed"] = "a"
            player.send_system_message(Color.GREEN, "A háló megtöltve 'A' csalival")
            return
        
        if args[0] == "b":
            vehicle.custom_vars["fisherman_feed"] = "b"
            player.send_system_message(Color.GREEN, "A háló megtöltve 'B' csalival")
            return
        
        if args[0] == "c":
            vehicle.custom_vars["fisherman_feed"] = "c"
            player.send_system_message(Color.GREEN, "A háló megtöltve 'C' csalival")
            return
        
        player.send_system_message(Color.ORANGE, "Ismeretlen csali!\nCsali típusok: a, b, c")
        return

    if functione == "leenged":
        if player.is_in_ashlar(-3359.9314, -2923.1167, -10, 3120.1536, 3026.4646, 10):
            player.send_system_message(Color.ORANGE, "Menj ki a nyílt vízre!")
            return
        
        if "fishingnet_in" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "A halászháló már le van engedve!")
            return
        
        if "fisherman_fishes" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "Van hal a hálóban, előbb rakodd ki!")
            return
        
        vehicle.custom_vars["fishingnet_in"] = True
        vehicle.custom_vars["fisherman_fishes"] = 0
        vehicle.custom_vars["fisherman_time"] = datetime.datetime.now()
        vehicle.timers["fisherman_fish_calc"] = set_timer(calculate_fish, 1000, True, vehicle)

        player.send_system_message(Color.GREEN, "A háló leengedve!")
        player.apply_animation("GRENADE","WEAPON_throwu",4.1,0,1,1,0,0,1)
        return

    if functione in ["behuz","behúz"]:
        if not "fishingnet_in" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "A halászháló nincs leengedve!")
            return
        
        if not "fisherman_fishes" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "A halászhálóban nincs hal!")
            return
        
        if ((datetime.datetime.now() - vehicle.custom_vars["fisherman_time"]).total_seconds() / 60) > 30:
            vehicle.custom_vars["fisherman_fishes"] = 0
            player.send_system_message(Color.ORANGE, "A halászháló kiszakadt!")
        else:
            player.send_system_message(Color.GREEN, "A háló behúzva! Nézd meg a tartalmát: /halasz tartalom")
            
        kill_timer(vehicle.timers["fisherman_fish_calc"])
        del vehicle.custom_vars["fishingnet_in"]
        del vehicle.custom_vars["fisherman_time"]
        del vehicle.timers["fisherman_fish_calc"]
        return

    if functione == "tartalom":
        if "fishingnet_in" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "A halászháló le van engedve!")
            return
        if not "fisherman_fishes" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "A halászhálóban nincs hal!")
            return
        
        dialog = Dialog.create(DialogStyle.MSGBOX,"Háló Tartalom", f"A hálóban található {vehicle.custom_vars["fisherman_fishes"]}db hal","Ok","")
        player.show_dialog(dialog)
        return

    if functione == "kirakod":

        if "fishingnet_in" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "A halászháló le van engedve!")
            return
        
        if not "fisherman_fishes" in vehicle.custom_vars:
            player.send_system_message(Color.ORANGE, "A halászhálóban nincs hal!")
            del vehicle.custom_vars["fisherman_fishes"]
            return
        
        if not player.is_in_range_of_point( 5.0, 2733.3801,-2319.6770,0.6904):
            player.send_system_message(Color.ORANGE, "Nem vagy a kirokodási pontnál!\nA pozíció jelölve a térképen!")
            player.set_checkpoint(2733.3801,-2319.6770,0.6904, 5.0)
            return
        
        fishmoney = vehicle.custom_vars["fisherman_fishes"] * 155
        player.add_payment(fishmoney)
        del vehicle.custom_vars["fisherman_fishes"]

    else:
        player.send_system_message(Color.RED, "Hibás típus!")
        player.send_system_message(Color.WHITE, "Típusok:  etetoanyag, leenged, behuz, tartalom, kirakod")
        return

def calculate_fish(vehicle: Vehicle):

    hrand = random.randint(1,100)
    hour = datetime.datetime.now().hour
    vX, vY, vZ = vehicle.get_velocity()
    speed = ((vX ** 2 + vY ** 2 + vZ ** 2) ** 0.5) * 100.0 * 1.63
    
    if speed > 10 and "fishingnet_in" in vehicle.custom_vars:
        if 19 <= hour < 22:
            if hrand <= 40:
                pass
            elif hrand >= 75:
                pass
            else:
                vehicle.custom_vars["fisherman_fishes"] += 1
        elif 2 <= hour < 6:
            if vehicle.custom_vars["fisherman_feed"] == 2:
                if hrand <= 30:
                    pass
                elif hrand >= 85:
                    pass
                else:
                    vehicle.custom_vars["fisherman_fishes"] += 1
            else:
                if hrand <= 30:
                    pass
                elif hrand >= 80:
                    pass
                else:
                    vehicle.custom_vars["fisherman_fishes"] += 1
        elif 6 <= hour < 11:
            if vehicle.custom_vars["fisherman_feed"] == 3:
                if hrand <= 40:
                    pass
                elif hrand >= 75:
                    pass
                else:
                    vehicle.custom_vars["fisherman_fishes"] += 1
            else:
                if hrand <= 40:
                    pass
                elif hrand >= 70:
                    pass
                else:
                    vehicle.custom_vars["fisherman_fishes"] += 1
        elif 11 <= hour < 15:
            if hrand <= 40:
                pass
            elif hrand >= 60:
                pass
            else:
                vehicle.custom_vars["fisherman_fishes"] += 1
        elif 15 <= hour < 19:
            if hrand <= 40:
                pass
            elif hrand >= 70:
                pass
            else:
                vehicle.custom_vars["fisherman_fishes"] += 1
        else:  # if h >= 22
            if vehicle.custom_vars["fisherman_feed"] == 2:
                if hrand <= 40:
                    pass
                elif hrand >= 85:
                    pass
                else:
                    vehicle.custom_vars["fisherman_fishes"] += 1
            else:
                if hrand <= 40:
                    pass
                elif hrand >= 80:
                    pass
                else:
                    vehicle.custom_vars["fisherman_fishes"] += 1