from python.model.server import Player
from python.logging import exception_logger
from python.utils.enums.translation_keys import TranslationKeys
from ..functions import log_ac
from ..notifier import anti_cheat_notify_player, anti_cheat_notify

@Player.mods_detected
def mods_detected(player: Player):
    player: Player = Player.get_registry_item(player.id)

    if player and player.variables and not player.variables.ac_detection["mods"]:
        player.variables.ac_detection["mods"] = True
        anti_cheat_notify_player(player, TranslationKeys.MODSDETECTED)
        anti_cheat_notify(TranslationKeys.MODSDETECTEDADMIN, False, True, player.name)
        log_ac(TranslationKeys.MODSDETECTEDADMIN, player.name)
