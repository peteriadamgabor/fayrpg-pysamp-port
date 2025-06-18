from python.jobs.crab_fisherman.events import show_icon_cages
from python.model.server import Player
from python.model.server import Vehicle
from python.logging.loggers import exception_logger
from python.utils.enums.colors import Color

from pysamp import set_timer
from python.model.server import Player
from python.model.server import Vehicle

from python.dialogtree import DialogTree
from python.dialogtree import ConfirmNode
from datetime import datetime, timedelta


@exception_logger.catch
@Player.on_enter_vehicle # type: ignore
@Player.using_registry
def on_enter_vehicle(player: Player, vehicle: Vehicle, is_passenger: bool):
    vehicle = Vehicle.get_registry_item(int(vehicle.id))

    if vehicle:
        show_icon_cages(player, vehicle)

        if not is_passenger:

            need_remove = False
            x, y, z = player.get_pos()

            if not vehicle.is_registered:
                player.send_system_message(Color.RED, "Hibás autó, nincs nyílvántartva!")
                return

            if vehicle.job_id is not None and vehicle.job_id != player.job:
                need_remove = True
                player.send_system_message(Color.RED, "Ez egy munkajármű! Nem használhatod!")
                
            if vehicle.fraction is not None and vehicle.fraction.id != player.fraction.id:
                need_remove = True
                player.send_system_message(Color.RED, "Ez egy frakció jármű!")
            
            if vehicle.is_rentable:
                if vehicle.renter is None:
                    show_rent_dilalog(player, vehicle)
                elif vehicle.renter.id != player.id:
                    need_remove = True
                    player.send_system_message(Color.RED, "Ezt a járművet nem Te bérled!")
                else:
                    pass

            if need_remove:
                player.remove_from_vehicle()
                player.set_pos(x, y, z + 2)
        
@exception_logger.catch
def show_rent_dilalog(player: Player, vehicle: Vehicle):

    dialog_tree: DialogTree | None = DialogTree()

    rent_conent: str = "{{00C0FF}}" + "Bérlés ára: " + "{{FFFFFF}}" + f"{vehicle.rent_price} Ft\n" "{{00C0FF}}"+ "Bérlés Időtartama: "+ "{{FFFFFF}}"+ f"{vehicle.rent_time} perc\n" +"{{FF0000}}" +" Ki kívánja bérelni?"
    rent_confirm: ConfirmNode = ConfirmNode("rent_confirm", rent_conent, "Kibérel", "Mégsem", f"Jármű bérlés - {vehicle.plate}")

    rent_confirm.response_handler = rent_car
    rent_confirm.response_handler_parameters = vehicle,

    dialog_tree.add_root(rent_confirm)
    dialog_tree.show_root_dialog(player)


@exception_logger.catch
@Player.using_registry
def rent_car(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    vehicle: Vehicle = args[0]

    if not bool(response):
        x, y, z = player.get_pos()
        player.remove_from_vehicle()
        player.set_pos(x, y, z + 2)
        return

    if not player.transfer_money(vehicle.rent_price):
        return

    player.send_system_message(Color.GREEN, f"Sikeresen kibérelted a járművet {vehicle.rent_time} percig")
    vehicle.renter = player
    vehicle.is_rented = True
    vehicle.rent_started = datetime.now()
    vehicle.rent_end = vehicle.rent_started + timedelta(minutes=vehicle.rent_time)

    vehicle.timers["rent_timer"] = set_timer(end_rent, vehicle.rent_time * 60 * 1000, False, vehicle)


@exception_logger.catch
def end_rent(vehicle: Vehicle):
    player: Player | None = vehicle.renter

    if player is None or player.get_vehicle() is None:
        return

    if player.get_vehicle().id == vehicle.id:
        x, y, z = player.get_pos()
        player.remove_from_vehicle()
        player.set_pos(x, y, z + 2)

    vehicle.renter = None
    vehicle.is_rented = False
    vehicle.rent_started = None
    vehicle.engine = 0
    del vehicle.timers["rent_timer"]