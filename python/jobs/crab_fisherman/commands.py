import datetime
import random

from pysamp.dialog import Dialog
from pystreamer import create_dynamic_object, destroy_dynamic_map_icon
from pystreamer.dynamicobject import DynamicObject
from python.model.server import Player
from python.model.server import CrabCage
from python.logging.loggers import exception_logger
from python.utils.enums.colors import Color
from python.utils.enums.dialog_style import DialogStyle
from python.model.server import Vehicle
from pysamp import kill_timer, set_timer
from python.utils.enums.jobs import JobsTypeEnum
from python.utils.helper.python import try_parse_int

@Player.command
@Player.using_registry
@exception_logger.catch
def rakhalasz(player: Player, functione: str = "", cage: int = 0, *args):

    if functione == "":
        player.send_system_message(Color.WHITE, "Használat: /rakhalasz [tipus] [ketrec (1-5)]")
        player.send_system_message(Color.WHITE, "Típusok:  etetoanyag, leenged, behuz, tartalom, kirakod")
        return

    if player.job != JobsTypeEnum.FISHERMAN:
        player.send_system_message(Color.ORANGE, "Nem vagy halász!")
        return
    
    if player.is_in_any_vehicle():
        player.send_system_message(Color.ORANGE, "Volán mögül nem használhatod!")
        return

    vehicle : Vehicle | None = player.get_nearest_vehicle(5, 453)

    if not vehicle:
        player.send_system_message(Color.ORANGE, "Nem vagy rákhalászhajón!")
        return
    

    if player.in_duty:
        player.send_system_message(Color.ORANGE, "Szolgálatban nem lehet!")
        return
    
    if (cage := try_parse_int(cage)) is None:
        player.send_system_message(Color.ORANGE, "Számmal kell megadni!")
        return
    
    if cage < 1 or cage > 5:
        player.send_system_message(Color.ORANGE, "Nem megfelelő ketrec!")
        return
    else:
        if not "crab_cages" in vehicle.custom_vars:
            vehicle.custom_vars["crab_cages"] = [
                CrabCage(0),
                CrabCage(1),
                CrabCage(2),
                CrabCage(3),
                CrabCage(4)
            ]
    
    cage = cage -1

    if functione in ["etetoanyag","etetőanyag"]:
        if player.is_in_ashlar(-3359.9314, -2923.1167, -10, 3120.1536, 3026.4646, 10):
            player.send_system_message(Color.ORANGE, "Menj ki a nyílt vízre!")
            return
        
        if vehicle.custom_vars["crab_cages"][cage].in_water:
            player.send_system_message(Color.ORANGE, "A ketrec le van engedve!")
            return
        
        if len(args) == 0:
            player.send_system_message(Color.ORANGE, "Ismeretlen csali!\nCsali típusok: csiga, kagyló, halcafat")
            return
        
        if args[0] == "csiga":
            vehicle.custom_vars["crab_cages"][cage].bait = 0
            player.send_system_message(Color.GREEN, "A ketrec megtöltve csigával")
            return
        
        if args[0] == "kagyló":
            vehicle.custom_vars["crab_cages"][cage].bait = 1
            player.send_system_message(Color.GREEN, "A ketrec megtöltve kagylóval")
            return
        
        if args[0] == "halcafat":
            vehicle.custom_vars["crab_cages"][cage].bait = 2
            player.send_system_message(Color.GREEN, "A ketrec megtöltve halcafattal")
            return
        
        player.send_system_message(Color.ORANGE, "Ismeretlen csali!\nCsali típusok: csiga, kagyló, halcafat")
        return

    if functione == "leenged":
        if player.is_in_ashlar(-3359.9314, -2923.1167, -10, 3120.1536, 3026.4646, 10):
            player.send_system_message(Color.ORANGE, "Menj ki a nyílt vízre!")
            return
        
        if vehicle.custom_vars["crab_cages"][cage].in_water:
            player.send_system_message(Color.ORANGE, "A ketrec már le van engedve!")
            return
        
        if vehicle.custom_vars["crab_cages"][cage].crabs > 0:
            player.send_system_message(Color.ORANGE, "Van rák a ketrecben, előbb rakodd ki!")
            return

        xx,yy,zz = player.get_pos()
        xs,ys = player.get_x_y_in_front_of(2)
        vehicle.custom_vars["crab_cages"][cage].in_water = True
        vehicle.custom_vars["crab_cages"][cage].time = datetime.datetime.now()
        vehicle.custom_vars["crab_cages"][cage].pos_x = xx
        vehicle.custom_vars["crab_cages"][cage].pos_y = yy
        vehicle.custom_vars["crab_cages"][cage].pos_z = zz
        vehicle.custom_vars["crab_cages"][cage].timer = set_timer(calculate_crabs, 1000, True, vehicle.custom_vars["crab_cages"][cage])
        vehicle.custom_vars["crab_cages"][cage].object = DynamicObject.create(918, xs, ys, 0, 0, 0, 0, -1, 0, -1)

        player.apply_animation("GRENADE","WEAPON_throwu",4.1,0,1,1,0,0,1)
        player.send_system_message(Color.GREEN, "A ketrec leengedve!")
        return

    if functione in ["behuz","behúz"]:
        if not vehicle.custom_vars["crab_cages"][cage].in_water:
            player.send_system_message(Color.ORANGE, "A ketrec nincs leengedve!")
            return
        
        if vehicle.custom_vars["crab_cages"][cage].crabs <= 0:
            player.send_system_message(Color.ORANGE, "A ketrecben nincs rák!")
            return
        if not player.is_in_range_of_point(10,vehicle.custom_vars["crab_cages"][cage].pos_x,vehicle.custom_vars["crab_cages"][cage].pos_y,vehicle.custom_vars["crab_cages"][cage].pos_z):
            player.send_system_message(Color.ORANGE, "Nincs ketrec a közelben!")
            return
        
        if ((datetime.datetime.now() - vehicle.custom_vars["crab_cages"][cage].time).total_seconds() / 60) > 30:
            vehicle.custom_vars["crab_cages"][cage].crabs = 0
            player.send_system_message(Color.ORANGE, "A ketrec tönkrement!")
        else:
            player.send_system_message(Color.GREEN, "A ketrec behúzva! Nézd meg a tartalmát: /rakhalasz [ketrec] tartalom")

        vehicle.custom_vars["crab_cages"][cage].in_water = False
        vehicle.custom_vars["crab_cages"][cage].object.destroy()
        kill_timer(vehicle.custom_vars["crab_cages"][cage].timer)
        return

    
    if functione == "tartalom":

        if vehicle.custom_vars["crab_cages"][cage].in_water:
            player.send_system_message(Color.ORANGE, "A ketrec le van engedve!")
            return
        
        if vehicle.custom_vars["crab_cages"][cage].crabs <= 0:
            player.send_system_message(Color.ORANGE, "A ketrecben nincs rák!")
            return
            
        if vehicle.custom_vars["crab_cages"][cage].bait == 0:
            dialog = Dialog.create(DialogStyle.MSGBOX,"Ketrec Tartalom", f"A ketrecben található {vehicle.custom_vars["fisherman_fishes"]}db Homár","Ok","")
        elif vehicle.custom_vars["crab_cages"][cage].bait == 1:
            dialog = Dialog.create(DialogStyle.MSGBOX,"Ketrec Tartalom", f"A ketrecben található {vehicle.custom_vars["fisherman_fishes"]}db Languszta","Ok","")
        else:
            dialog = Dialog.create(DialogStyle.MSGBOX,"Ketrec Tartalom", f"A ketrecben található {vehicle.custom_vars["fisherman_fishes"]}db Tarisznyarák","Ok","")

        player.show_dialog(dialog)
        return

    if functione == "kirakod":

        if vehicle.custom_vars["crab_cages"][cage].in_water:
            player.send_system_message(Color.ORANGE, "A ketrec le van engedve!")
            return
        
        if vehicle.custom_vars["crab_cages"][cage].crabs <= 0:
            player.send_system_message(Color.ORANGE, "A ketrecben nincs rák!")
            return
        
        if not player.is_in_range_of_point( 5.0, 2672.3599,-2325.6094,0.9024):
            player.send_system_message(Color.ORANGE, "Nem vagy a kirokodási pontnál!\nA pozíció jelölve a térképen!")
            player.set_checkpoint(2672.3599,-2325.6094,0.9024, 5.0)
            return
        
        if vehicle.custom_vars["crab_cages"][cage].bait == 0:
            crabmoney = vehicle.custom_vars["crab_cages"][cage].crabs * 290
        elif vehicle.custom_vars["crab_cages"][cage].bait == 1:
            crabmoney = vehicle.custom_vars["crab_cages"][cage].crabs * 320
        else:
            crabmoney = vehicle.custom_vars["crab_cages"][cage].crabs * 210

        player.add_payment(crabmoney)
    
    else:
        player.send_system_message(Color.RED, "Hibás típus!")
        player.send_system_message(Color.WHITE, "Típusok:  etetoanyag, leenged, behuz, tartalom, kirakod")
        return

def calculate_rakok(hrandom, thresholds):
    for limit, value in thresholds:
        if hrandom <= limit:
            return value
    return 0

def calculate_crabs(cage: CrabCage):

    hrandom = random.randint(1, 100)
    h = datetime.datetime.now().hour

    # Időszakokra vonatkozó küszöbértékek
    thresholds_by_time = {
        range(3, 7): [(10, 0), (20, 1), (50, 3), (80, 5), (100, 7)],
        range(7, 13): [(30, 0), (60, 1), (80, 3), (90, 5), (100, 7)],
        range(13, 20): [(40, 0), (70, 1), (80, 3), (90, 5), (100, 7)],
        range(20, 24): [(20, 0), (50, 1), (80, 3), (90, 5), (100, 7)]
    }

    # Megfelelő küszöbértékek kiválasztása az idő alapján
    thresholds = None
    for time_range, thresh in thresholds_by_time.items():
        if h in time_range:
            thresholds = thresh
            break

    if thresholds:
        cage.crabs += calculate_rakok(hrandom, thresholds)
        
