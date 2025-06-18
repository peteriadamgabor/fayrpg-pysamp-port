
from pysamp import create_3d_text_label
from pystreamer.dynamictextlabel import DynamicTextLabel
from python.model.server import Player
from python.utils.enums.colors import Color
from python.utils.vars import ADMIN_PLAYERS
from ..functions import check_player_role_permission

@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def mc(player: Player, *args):
    if len(args) == 0:
        return

    send_msg = f'*MC* {player.role.name} {player.name}: {" ".join(args)}'

    for _, admin in ADMIN_PLAYERS.items():
        admin.send_client_message(Color.YELLOW, send_msg)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def asay(player: Player, *args):
    if len(args) == 0:
        return

    send_msg = f'{player.role.name} {player.name}: {" ".join(args)}'

    for i in Player.get_registry_items():
        i.send_client_message(Color.LIGHTBLUE, send_msg)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def asayn(player: Player, *args):
    if len(args) == 0:
        return

    send_msg = f'{player.role.name}: {" ".join(args)}'

    for i in Player.get_registry_items():
        i.send_client_message(Color.LIGHTBLUE, send_msg)
