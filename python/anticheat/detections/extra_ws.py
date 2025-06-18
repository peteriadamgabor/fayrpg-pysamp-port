from python.model.server import Player
from python.logging import exception_logger
from python.utils.enums.translation_keys import TranslationKeys
from ..functions import log_ac
from ..notifier import anti_cheat_notify_player, anti_cheat_notify

@exception_logger.catch
@Player.extra_ws_detected
def extra_ws_detected(player: Player):
    anti_cheat_notify_player(player, TranslationKeys.EXTRAWSDETECTED)
    anti_cheat_notify(TranslationKeys.EXTRAWSDADMIN, False, True, player.name)
    log_ac(TranslationKeys.EXTRAWSDADMIN, player.name)
    player.kick()
