from python.model.server import Player as PlayerSRV

from python.utils.enums.translation_keys import TranslationKeys

from config import settings

from ..notifier import anti_cheat_notify_player, anti_cheat_notify

def tigger(player: PlayerSRV):
    player_ping: int = player.get_ping()

    if player_ping > settings.anti_cheat.ping.max:
        player.variables.ac_warns["ping"] += 1
        anti_cheat_notify_player(player, TranslationKeys.HIGHPING, player_ping, settings.anti_cheat.ping.max)

        if player.variables.ac_warns["ping"] >=  settings.anti_cheat.ping.max_warn:
            anti_cheat_notify(TranslationKeys.HIGHPINGKICK, settings.anti_cheat.ping.notify.player, settings.anti_cheat.ping.admin, player.name, player_ping, settings.anti_cheat.ping.max)
            player.kick()