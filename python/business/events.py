from .function import buy_business, list_car_catalog
from .function import enter_business
from .function import lock_business
from .function import sell_business

from python.model.server import Player, Business
from python.utils.helper.python import format_numbers

from python.dialogtree import ActionNode
from python.dialogtree import ListNode
from python.dialogtree import ConfirmNode
from python.dialogtree import DialogTree


@Player.using_registry
def on_player_pick_up_pickup_business(player: Player, business: Business) -> None:
    if business is None:
        return

    dialog_tree: DialogTree | None = DialogTree()

    enter_action: ActionNode = ActionNode("enter_action", "Belép")
    enter_action.close_in_end = True
    enter_action.response_handler = enter_business
    enter_action.response_handler_parameters = business,


    root_node: ListNode

    if not business.owner:
            root_node = ListNode("no_owner_root", "", "Kiválaszt", "Bezár", f"{business.name} | Tulajdonos: Nincs")

            buy_node_content: str = "{{FFFFFF}}Biztos meg akarja vásárolni a bizniszt {{b4a2da}} " + format_numbers(business.price) + " {{FFFFFF}}Ft ért?"

            buy_confirm: ConfirmNode = ConfirmNode("buy_confirm", buy_node_content, "Megvesz", "Mégsem", "Ház vásárlás", "Megvásárlás")

            buy_confirm.response_handler = buy_business
            buy_confirm.response_handler_parameters = business,

            root_node.add_child(enter_action)
            root_node.add_child(buy_confirm)

            dialog_tree.add_root(root_node)

    else:
        if business.owner.id == player.dbid:
                root_node: ListNode = ListNode("owned_root", "", "Kiválaszt", "Bezár", f"{business.name} | Tulajdonos: {business.owner.name.replace('_', ' ')}")

                sell_node_content: str = "{{FFFFFF}}Biztos elakarod adni a bizniszt {{b4a2da}} " + format_numbers(int(business.price * .75)) + " {{FFFFFF}}Ft ért?"
                sell_node = ConfirmNode("sell_node", sell_node_content, "Igen", "Nem", "Biznisz eladás", "Eladás")
                sell_node.response_handler=sell_business
                sell_node.response_handler_parameters=business,
                
                lock_action: ActionNode = ActionNode("lock_action", f"{'Kinyit' if business.locked else 'Bezár'}")
                lock_action.close_in_end = True
                lock_action.response_handler = lock_business
                lock_action.response_handler_parameters = business,

                root_node.add_child(enter_action)
                root_node.add_child(lock_action)
                root_node.add_child(sell_node)

                dialog_tree.add_root(root_node)

        else:
            root_node = ListNode("guest_root", "", "Kiválaszt", "Bezár", f"{business.name} | {business.owner.name}")
            
            root_node.add_child(enter_action)
            dialog_tree.add_root(root_node)

    if len(business.cars) > 0:
        car_node: ActionNode = ActionNode("car_node", "Autókatalógus")
        car_node.close_in_end = True
        car_node.response_handler = list_car_catalog
        car_node.response_handler_parameters = business.id,
        
        root_node.add_child(car_node)
    
    
    dialog_tree.show_root_dialog(player)
