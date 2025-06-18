from python.model.server import Player
from python.model.dto.teleport import Teleport
from python.utils.enums.colors import Color
from python.utils.enums.translation_keys import TranslationKeys


def handle_teleport_use(player: Player, teleport: Teleport) -> None:
    if player.check_used_teleport():
        return

    if player.have_hospital_time:
        player.send_system_message_multi_lang(Color.RED, TranslationKeys.INHOSPITAL)
        return

    if player.in_vehicle():
        return

    sound_id = 1 if teleport.to_interior != 0 or teleport.to_vw != 0 else 0

    player.play_sound(sound_id, 0.0, 0.0, 0.0)
    player.set_interior(teleport.to_interior)
    player.set_virtual_world(teleport.to_vw)
    player.set_pos(teleport.to_x, teleport.to_y, teleport.to_z)
    player.set_facing_angle(teleport.to_angel)
