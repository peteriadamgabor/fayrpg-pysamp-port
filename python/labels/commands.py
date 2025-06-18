
from pysamp.object import Object
from pystreamer.dynamicobject import DynamicObject
from python.admin.functions import check_player_role_permission, send_admin_action

from python.dialogtree import DialogTree
from python.dialogtree import ActionNode
from python.dialogtree import ListNode

from python.model.server import Player
from python.model.server import Labale

from python.utils.enums.colors import Color

@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def listlabels(player: Player):
    root_node: ListNode = ListNode("maps_root", "Szöveg\tSzín\tdd\n", "Kiválaszt", "Bezár", "3D Textek", True, True)
    tree: DialogTree = DialogTree()
    root_node.set_tree(tree)
    tree.add_root(root_node)

    for label in Labale.get_registry_items():
        display: str = f"{label.text}\t{label.color}\t{label.dd}"

        teleport_node: ActionNode = ActionNode("teleport_node", display)
        teleport_node.response_handler = teleport_to_label
        teleport_node.response_handler_parameters = label.x, label.y, label.z, label.interior, label.vw,
        teleport_node.close_in_end = True
        teleport_node.set_tree(tree)

        root_node.add_child(teleport_node)
    tree.show_root_dialog(player)

@Player.using_registry
def teleport_to_label(player: Player, response: int, list_item: int, input_text: str, x: float, y: float, z: float, interior: int, vw: int, *args):
    player.set_pos(x, y, z)
    player.set_interior(interior if interior != -1 else 0)
    player.set_virtual_world(vw if vw != -1 else 0)
