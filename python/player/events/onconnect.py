from datetime import datetime
from python import LogTypes
from python.model.server import Map
from python.model.server import Player
from python.discord import send_embed
from python.utils.enums.colors import Color
from python.logging import exception_logger, Logger


@exception_logger.catch
@Player.on_connect # type: ignore
def on_connect(player: Player):

    send_embed("Player connected", f"{player.get_name()} [{player.get_id()}] is connected the server from {player.get_ip()}", "ff8080")

    for serv_map in Map.get_registry_items():
        for i in serv_map.remove_objects:
            player.remove_building(*i)

    player.set_time(datetime.now().hour, datetime.now().minute)
    Logger.write_log(LogTypes.CONNECTION, f"{player.get_name()} csatlakozott a szerverre. IP: {player.get_ip()}")

    player.set_color(Color.WHITE)

    for i in Player.get_registry_items():
        try:
            target_player = i.get_color() & 0xFFFFFF00
            self_player = player.get_color() & 0xFFFFFF00

            player.set_marker(i, target_player)
            i.set_marker(player, self_player)

        except Exception as ex:
            print(ex)
