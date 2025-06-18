from typing import List

from python.model.database import CommandPermission as CommandPermissionDB
from python.model.database import role
from python.model.server import Player
from python.utils.vars import COMMAND_PERMISSIONS


def _check_permission(player_id: int, cmd_txt: str):

    player: Player = Player.from_registry_native(player_id)

    cmd_perm: CommandPermissionDB = COMMAND_PERMISSIONS.get(cmd_txt, None)
    player_role_perms: List[Permission] = player.role.permissions if player.role else None

    if cmd_perm and player_role_perms:
        permission = next((e for e in player_role_perms if e.permission_type.code == cmd_perm.permission_type.code), None)
        if permission:
            return permission.power >= cmd_perm.need_power

    return False


def check_permission(cmd_txt: str):
    return lambda player_id: _check_permission(player_id, cmd_txt)
