from python.model.server import Player
from python.logging import exception_logger
from python.utils.enums.translation_keys import TranslationKeys
from ..functions import log_ac
from ..notifier import anti_cheat_notify_player, anti_cheat_notify

@exception_logger.catch
@Player.sprint_hook_detected
def sprint_hook_detected(player: Player):
    anti_cheat_notify_player(player, TranslationKeys.SPRINTHOOKDETECTED)
    anti_cheat_notify(TranslationKeys.SPRINTHOOKADMIN, False, True, player.name)
    log_ac(TranslationKeys.SPRINTHOOKADMIN, player.name)
    player.kick()
