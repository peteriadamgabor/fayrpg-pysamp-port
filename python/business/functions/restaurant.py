from python.business.function import change_business_interior, eval_menu_item_use
from python.dialogtree.dialog_tree import DialogTree
from python.dialogtree.nodes.action import ActionNode
from python.dialogtree.nodes.confim import ConfirmNode
from python.dialogtree.nodes.list import ListNode

from python.model.server import Player, Business
from python.model.database import Business as BusinessDB
from python.model.database import Player as PlayerDB
from python.model.database import RestaurantMenu as RestaurantMenuDB

from python.utils.enums.colors import Color
from python.utils.globals import BUESSNES_VIRTUAL_WORD


from sqlalchemy import select
from python.server.database import BUSINESS_SESSION

from python.database import transactional_session
from python.utils.helper.python import format_numbers

def restaurant_nodes(player: Player):

    if player.virtual_world < BUESSNES_VIRTUAL_WORD:
        player.send_system_message_multi_lang(Color.RED, "Nem vagy étteremben!")
        return

    business: Business | None = Business.get_registry_item(player.virtual_world - BUESSNES_VIRTUAL_WORD)

    if not business:
        return

    if business.business_type.id not in [5, 6]:
        player.send_system_message_multi_lang(Color.RED, "Nem vagy étteremben!")
        return

    with transactional_session(BUSINESS_SESSION) as session:
        restaurant_menus: list[RestaurantMenuDB] = list(session.scalars(select(RestaurantMenuDB).join(BusinessDB).where(RestaurantMenuDB.business_id == business.id)).all())

        root_node: ListNode = ListNode("manu_root", "", "Kiválaszt", "Bezár", "Étlap")
        tree: DialogTree = DialogTree()
        root_node.set_tree(tree)
        tree.add_root(root_node)

        for restaurant_menu in restaurant_menus:
            menu_node: ActionNode = ActionNode("price_node", f"{restaurant_menu.name} - {format_numbers(restaurant_menu.price)} Ft")
            menu_node.response_handler = eval_menu_item_use
            menu_node.response_handler_parameters = (business.id, restaurant_menu.id)
            menu_node.close_in_end = True

            root_node.add_child(menu_node)

    tree.show_root_dialog(player)