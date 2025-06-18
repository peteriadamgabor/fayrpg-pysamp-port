from .functions import show_inventory

from python.model.server import Player
from python.utils.enums.colors import Color


@Player.command
@Player.using_registry
def taska(player: Player):

    player.load_items()

    if not player.items:
        player.send_client_message(Color.ORANGE, "(( Üres a táskád! ))")
        return

    show_inventory(player, False)