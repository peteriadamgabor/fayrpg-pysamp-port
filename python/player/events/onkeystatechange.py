import random

from python.model.server import Player
from python.model.server import Vehicle
from python.logging.loggers import exception_logger
from python.utils.enums.states import State
from python.vehicle.functions import handle_engine_switch


@exception_logger.catch
@Player.on_key_state_change  # type: ignore
@Player.using_registry
def on_key_state_change(player: Player, new_keys: int, old_keys: int):
    if (new_keys == 512 or new_keys == 520) and player.get_state() == State.DRIVER:
        vehicle: Vehicle = player.get_vehicle()
        vehicle.lights = int(not vehicle.lights)

    if new_keys == 640 and player.get_state() == State.DRIVER:
        vehicle: Vehicle = player.get_vehicle()
        handle_engine_switch(player, vehicle)

    if new_keys == 8 and player.get_state() == State.DRIVER:
        number = random.randint(0, 100)
        vehicle: Vehicle = player.get_vehicle()

        if vehicle.get_health() < 450.0 and (70 < number < 85):
            vehicle.engine = 0
            vehicle.get_damage_status()
            player.game_text("~r~Lefulladt az auto", 3000, 3)
