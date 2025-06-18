from python.model.server import Player, Vehicle
from python.utils.enums.colors import Color
from python.utils.enums.states import State
from python.utils.helper.python import try_parse_int
from python.vehicle.functions import handle_engine_switch


@Player.command
@Player.using_registry
def indit(player: Player):
    if player.get_state() != State.DRIVER:
        player.send_system_message(Color.RED, "Nem vagy sofor!")
        return

    vehicle: Vehicle = player.get_vehicle()
    handle_engine_switch(player, vehicle)


@Player.command
@Player.using_registry
def leallit(player: Player):
    if player.get_state() != State.DRIVER:
        player.send_system_message(Color.RED, "Nem vagy sofor!")
        return

    vehicle: Vehicle = player.get_vehicle()

    if vehicle.engine == 0:
        player.send_system_message(Color.WHITE, f"A motor nem jár!")
        return

    handle_engine_switch(player, vehicle)


@Player.command
@Player.using_registry
def rendszam(player: Player):
    if not player.in_vehicle():
        player.send_system_message(Color.RED, "Ez a járműben nem szerepel a rendszerben!")
        return

    vehicle: Vehicle = player.get_vehicle()

    player.send_system_message(Color.WHITE, f"Rendszám: {vehicle.plate}")

@Player.command
@Player.using_registry
def csomagtarto(player: Player, action: str = ""):
    vehicle: Vehicle = player.get_nearest_vehicle(7.0)

    if vehicle is None or player.in_vehicle():
        return
    
    if not action:
        player.send_system_message(Color.WHITE, "Ismeretlen típus!\nTípusok: kinyit, bezár, felnyit, becsuk, tartalom, berak")
        return
    
    if action == "felnyit":
        vehicle.trunk = 1
    
    elif action == "becsuk":
        vehicle.trunk = 0


@Player.command
@Player.using_registry
def motorhazteto(player: Player):
    vehicle: Vehicle = player.get_nearest_vehicle(7.0)

    if vehicle is None or player.in_vehicle():
        return
    
    vehicle.hood = not vehicle.hood


@Player.command
@Player.using_registry
def limiter(player: Player, limit: int):

    if player.get_state() != State.DRIVER:
        player.send_system_message(Color.RED, "Nem vagy sofőr!")
        return
    
    vehicle: Vehicle = player.get_vehicle()

    if vehicle.get_speed() > 0:
        player.send_system_message(Color.RED, "Csak álló helyzetben állítható!")
        return

    c_value: int | None = try_parse_int(limit)

    if c_value is None:
        player.send_system_message(Color.RED, "Számmal kell megadni!")
        return

    if vehicle.model.max_speed < c_value or c_value < 0:
        player.send_system_message(Color.RED, "Érvénytelen limiter!")
        return

    vehicle.limiter = c_value / vehicle.model.max_speed if c_value > 0 else 0

    if c_value > 0 and c_value:
        player.send_system_message(Color.GREEN, f"Sebesség limiter bekapcsolva! Limiter {c_value} km/h")

    else:
        player.send_system_message(Color.GREEN, f"Sebesség limiter kikapcsolva!")

