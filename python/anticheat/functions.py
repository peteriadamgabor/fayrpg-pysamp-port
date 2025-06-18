from python.utils.enums.log_type import LogTypes
from python.logging import Logger
from python.model.server import Player as PlayerSRV
from python.utils.enums.colors import Color
from python.utils.enums.translation_keys import TranslationKeys

from python.language import get_translated_text

from config import settings


def log_ac(translation_key: str, *args):
    log_msg = get_translated_text(translation_key, settings.server.language, *args)
    Logger.write_log(LogTypes.ANTI_CHEAT, log_msg)


def boradcast_ban_msg(banned_player: PlayerSRV, admin: PlayerSRV | None, lenght: int, lenght_type: str, *args):

    text = None

    if lenght_type.lower() in settings.server.ban_lenght_types.day.names.lower():
        text = get_translated_text(TranslationKeys.DAY, settings.server.language)
         
    elif lenght_type.lower() in settings.server.ban_lenght_types.hour.names.lower():
        text = get_translated_text(TranslationKeys.HOUR, settings.server.language)
         
    elif lenght_type.lower() in settings.server.ban_lenght_types.minute.names.lower():
        text = get_translated_text(TranslationKeys.MINUTE, settings.server.language)

    if admin:
        reason = get_translated_text(TranslationKeys.BANMSG, settings.server.language, admin.name, banned_player.name, lenght, text, " ".join(args))
    
    else:
        reason = get_translated_text(TranslationKeys.SYSTEMBANMSG, settings.server.language, banned_player.name, lenght, text, " ".join(args))

    for player in PlayerSRV.get_registry_items():
        player.send_client_message(Color.LIGHT_RED, reason)