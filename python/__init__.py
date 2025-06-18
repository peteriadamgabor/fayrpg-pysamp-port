import samp #type: ignore
samp.config(encoding='cp1250')

from pysamp import on_gamemode_init, on_gamemode_exit
from pysamp.commands import dispatcher as main_dispatcher
from pysamp.callbacks import hook

import importlib

from sqlalchemy.orm import close_all_sessions

from python.utils.vars import PLAYER_COMMAND
from python.language import get_translated_text
from python.utils.enums.log_type import LogTypes
from python.utils.enums.translation_keys import TranslationKeys
from python.server.functions import server_start, set_up_py_samp
from python.logging import exception_logger, Logger
from python.model.server import Player
from python.utils.enums.colors import Color

from config import settings

for module in settings.server.modul_list:  #type: ignore
    importlib.import_module(f"python.{module.strip()}")


@exception_logger.catch # type: ignore
@on_gamemode_init
def server_init():
    set_up_py_samp()
    server_start()


@exception_logger.catch # type: ignore
@on_gamemode_exit
def server_stop():
    close_all_sessions()


def OnPlayerCommandText(playerid: int, cmdtext: str):
    handle_result: bool = False

    command_parst: list[str] = cmdtext.split(" ")
    command: str = command_parst[0].lower()
    command_args: str = " ".join(command_parst[1:])

    PLAYER_COMMAND[playerid] = command[1:]

    cmd_player: Player | None = Player.get_registry_item(playerid)

    if not cmd_player:
        return True

    Logger.write_log(LogTypes.COMMAND,
                    f"{cmdtext} - {cmd_player.get_name()}",
                     cmd_player.session_token)

    try:
        handle_result = main_dispatcher.handle(playerid, f"{command} {command_args}")
    except Exception as ex:
        exception_logger.exception(ex)

    if not handle_result:
        cmd_player.send_client_message(Color.WHITE, get_translated_text(TranslationKeys.UNKNOWCOMMAND))

    return True

hook()
