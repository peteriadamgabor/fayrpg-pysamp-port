from python.model.server import Player
from ..functions import check_player_role_permission
from python.model.server import House
from python.utils.enums.colors import Color
from python.utils.decorator import cmd_arg_converter
from python.utils.enums.translation_keys import TranslationKeys


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
@cmd_arg_converter
def gotohouse(player: Player, house_number: int):

   if house_number is str:
      player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
      return

   house = House.get_registry_item(house_number)

   player.set_pos(house.entry_x, house.entry_y, house.entry_z)
   player.set_interior(0)
   player.set_virtual_world(0)

   player.send_system_message(Color.GREEN, f"Sikeresen a(z) {house.id} számű házhoz teleportáltál!")