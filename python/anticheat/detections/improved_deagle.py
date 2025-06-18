from python.model.server import Player
from python.logging import exception_logger
from python.utils.enums.translation_keys import TranslationKeys
from ..functions import log_ac
from ..notifier import anti_cheat_notify_player, anti_cheat_notify

@exception_logger.catch
@Player.improved_deagle_detected
def improved_deagle_detected(player: Player):
    anti_cheat_notify_player(player, TranslationKeys.IMPROVEDDEAGLEDETECTED)
    anti_cheat_notify(TranslationKeys.IMPROVEDDEAGLEADMIN, False, True, player.name)
    log_ac(TranslationKeys.IMPROVEDDEAGLEADMIN, player.name)
    player.kick()
