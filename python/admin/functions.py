from typing import Optional
from pyeSelect.eselect import MenuItem
from python import exception_logger, PLAYER_COMMAND
from python.language import get_translated_text
from python.model.database import CommandPermission, Command
from python.model.server import Player, Vehicle
from python.server.database import MAIN_SESSION
from python.utils.enums.colors import Color
from python.utils.vars import ADMIN_PLAYERS

from config import settings


@Player.using_registry
@exception_logger.catch
def check_player_role_permission(player: Player) -> bool:
    if player.role is None:
        return False

    cmd_txt: str | None = PLAYER_COMMAND.pop(player.id, None)

    if cmd_txt is None:
        return False

    with (MAIN_SESSION() as session):
        command_permission: Optional[CommandPermission] = session.query(CommandPermission).join(Command).filter(Command.cmd_txt == cmd_txt).one_or_none()

        if command_permission is None:
            return True

        return command_permission.need_power <= player.role.power


@exception_logger.catch
def send_admin_action(admin: Player, msg: str, skip_power_chek: bool = False) -> None:
    if admin.role is None:
        return
    send_msg = f'*ACMD* {admin.role.name} {admin.name} {msg}'

    sender_admin_power: int = admin.role.power

    for _, player in ADMIN_PLAYERS.items():
        if player.role is None:
            continue
            
        if skip_power_chek or sender_admin_power <= player.role.power:
            player.send_client_message(Color.LIGHT_RED, send_msg)


@exception_logger.catch
def send_admin_action_multi_lang(admin: Player, msg_key: str, skip_power_chek: bool = False, *args) -> None:
    if admin.role is None:
        return
    
    send_msg = f'*ACMD* {admin.role.name} {admin.name} '

    sender_admin_power: int = admin.role.power

    for _, player in ADMIN_PLAYERS.items():
        if player.role is None:
            continue
            
        if skip_power_chek or sender_admin_power <= player.role.power:
            msg = send_msg + get_translated_text(msg_key, settings.server.language, *args) # type: ignore
            player.send_client_message(Color.LIGHT_RED, msg)


@exception_logger.catch
def send_acmd(msg: str, power: int = 0) -> None:
    send_msg = f'*ACMD* {msg}'

    for _, player in ADMIN_PLAYERS.items():
        notified_power = next((e for e in player.role.permissions if e.permission_type.code == 'admin_power'), None)

        if notified_power.power >= power:
            player.send_client_message(Color.LIGHT_RED, send_msg)


@exception_logger.catch
@Player.using_registry
def spawn_admin_car(player: Player, menu_item: MenuItem):
    (_, _, z) = player.get_pos()
    angle: float = player.get_facing_angle() + 90 if player.get_facing_angle() < 0 else player.get_facing_angle() - 90
    x, y = player.get_x_y_in_front_of(5)

    color1, color2 = menu_item.color_1, menu_item.color_2

    plate: str = "NINCS"
    Vehicle.create(menu_item.model_id, x, y, z, angle, int(color1), int(color2), -1, plate)


@Player.using_registry
def change_skin(player: Player, menu_item: MenuItem):
    player.change_skin(menu_item.model_id)


@Player.using_registry
def add_record_rout_point(player: Player):
    player.set_checkpoint(*player.get_pos(), size=5)
    record_list = player.custom_vars["recorded_rout_points"]
    record_list.append(player.get_pos())
    player.custom_vars["recorded_rout_points"] = record_list
