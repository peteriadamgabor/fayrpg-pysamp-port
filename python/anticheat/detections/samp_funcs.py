from python.model.server import Player
from python.logging import exception_logger
from python.utils.enums.translation_keys import TranslationKeys
from ..functions import log_ac
from ..notifier import anti_cheat_notify_player, anti_cheat_notify

@exception_logger.catch
@Player.samp_funcs_detected
def samp_funcs_detected(player: Player):
    anti_cheat_notify_player(player, TranslationKeys.SAMPFUNCSDETECTED)
    anti_cheat_notify(TranslationKeys.SAMPFUNCSDETECTEDADMIN, False, True, player.name)
    log_ac(TranslationKeys.SAMPFUNCSDETECTEDADMIN, player.name)
    player.kick()