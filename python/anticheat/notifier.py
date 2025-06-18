from python.utils.enums.colors import Color
from python.model.server import Player as PlayerSRV

from python.utils.vars import ADMIN_PLAYERS
from python.language import get_translated_text


def anti_cheat_notify(notification: str, notify_player: bool, notify_admin: bool, *args):
    if notify_player:
        sending_msg = "{{FB0000}}[ANTI-CHEAT]{{FFFF00}} {0}"
        for player in PlayerSRV.get_registry_items():
            trans_text = get_translated_text(notification, player.language, *args)
            player.send_client_message(Color.YELLOW, sending_msg.format(trans_text))

    if notify_admin:
        sending_msg = "*ACMD-AC* {0}"
        for _, admin in ADMIN_PLAYERS.items():
            trans_text = get_translated_text(notification, admin.language, *args)
            admin.send_client_message(Color.LIGHT_RED, sending_msg.format(trans_text))

def anti_cheat_notify_player(player: PlayerSRV, notification: str, *args):
    sending_msg = "{{FB0000}}[ANTI-CHEAT]{{FFFF00}} {0}"
    
    lang = player.language if player.language else "hu"

    trans_text = get_translated_text(notification, lang, *args)
    player.send_client_message(Color.YELLOW, sending_msg.format(trans_text))
