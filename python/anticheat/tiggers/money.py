from python.model.database import Ban
from python.model.server import Player as PlayerSRV

from python.language import get_translated_text

from python.utils.enums.translation_keys import TranslationKeys

from ..notifier import anti_cheat_notify

from ..functions import boradcast_ban_msg

def tigger(player: PlayerSRV):
    if player.get_money() > 0:
        reason = get_translated_text(TranslationKeys.MONEYHACKBAN)

        Ban.create(player.dbid, None, player.get_ip(), 365, "day", reason)

        anti_cheat_notify(TranslationKeys.MONEYHACK, False, True, player.name, player.get_money())
        boradcast_ban_msg(player, None, 365, "day", reason)

        player.kick()
