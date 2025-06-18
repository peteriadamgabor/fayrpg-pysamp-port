from python.model.server import Player
from python.model.server import ReportCategory

from python.utils.enums.colors import Color

from python.admin.functions import check_player_role_permission, send_admin_action

from python.report.functions import change_admin_category

from python.dialogtree import ActionNode
from python.dialogtree import ListNode
from python.dialogtree import DialogTree

@Player.command(aliases=('v',), requires=[check_player_role_permission])
@Player.using_registry
def valasz(player: Player, target: str | int, *args):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        return

    category = player.report_category

    if category == "AFK":
        player.send_system_message(Color.ORANGE, "AFK vagy nem válaszolhatsz!")
        return
    
    msg: str = " ".join(args)

    answer = f"*{category}* {player.role.name} {player.name} válasza: {msg}" # type: ignore
    player.send_client_message(Color.YELLOW, answer)

    acmd: str = f"válaszolt neki: {target_player.name}[{target_player.id}]: {msg}"
    send_admin_action(player, acmd, True)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def jelentesek(player: Player):
    dialog_tree: DialogTree | None = DialogTree()
    report_list_node: ListNode = ListNode("report_list_node", "", "Kiválaszt", "Bezár", "Válassz kategórát")
    
    for value in ReportCategory.get_registry_items():
        node_content: str = f"{value.name}"
        node: ActionNode = ActionNode("node", node_content)

        node.response_handler = change_admin_category # type: ignore
        node.response_handler_parameters = value.code,
        node.close_in_end = True

        report_list_node.add_child(node)


    dialog_tree.add_root(report_list_node) # type: ignore
    dialog_tree.show_root_dialog(player)
