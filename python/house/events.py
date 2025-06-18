from python.dialogtree import ActionNode
from python.dialogtree import ListNode
from python.dialogtree import ConfirmNode
from python.dialogtree import InputNode
from python.dialogtree import DialogTree

from .functions import print_house_info
from .functions import buy_house
from .functions import enter_house
from .functions import lock_house
from .functions import sell_house
from .functions import cancel_rent
from .functions import rent_house
from .functions import extend_rent
from .functions import set_spawn_house
from .functions import crack_lock_house

from python.model.server import House, Player
from python.utils.helper.python import format_numbers

@Player.using_registry
def on_player_pick_up_pickup_house(player: Player, house: House):
    if house is None:
        return

    dialog_tree: DialogTree | None = DialogTree()

    info_action: ActionNode = ActionNode("info_action", display="Információ")
    info_action.response_handler = print_house_info
    info_action.response_handler_parameters = house,

    enter_action: ActionNode = ActionNode("enter_action", "Belép")
    enter_action.response_handler = enter_house
    enter_action.response_handler_parameters = house,

    lock_action: ActionNode = ActionNode("lock_action", f"{'Kinyit' if house.locked else 'Bezár'}")
    lock_action.response_handler = lock_house
    lock_action.response_handler_parameters = house,

    crack_lock_action: ActionNode = ActionNode("crack_lock_action", "Zár feltörése")
    crack_lock_action.response_handler = crack_lock_house
    crack_lock_action.response_handler_parameters = house,
    crack_lock_action.close_in_end = True

    if not house.owner:
        if house.type == 0:
            buy_house_root: ListNode = ListNode("no_owner_root", "", "Kiválaszt", "Bezár", "Eladó ház")

            buy_node_content: str = "{{FFFFFF}}Biztos meg akarja vásárolni a házat {{b4a2da}} " + format_numbers(house.price + house.house_type.price) + " {{FFFFFF}}Ft ért?"

            buy_confirm: ConfirmNode = ConfirmNode("buy_confirm", buy_node_content, "Megvesz", "Mégsem", "Ház vásárlás", "Megvásárlás")

            buy_confirm.response_handler = buy_house
            buy_confirm.response_handler_parameters = house,

            buy_house_root.add_child(info_action)
            buy_house_root.add_child(buy_confirm)

            dialog_tree.add_root(buy_house_root)

        if house.type == 1:
            rent_house_root: ListNode = ListNode("no_rented_root", "", "Kiválaszt", "Bezár", "Bérelhető ház")

            rent_node_content: str = "{{FFFFFF}}Hány napig szertné bérbe venni a lakást? {{FFFFFF}} \nÁr: {{b4a2da}} " + format_numbers(house.price) + " {{FFFFFF}} Ft / nap"
            rent_node: InputNode = InputNode("rent_node", rent_node_content, "Bérlés", "Mégsem", "Ház vásárlás", "Bérlés")

            rent_node.response_handler = rent_house
            rent_node.response_handler_parameters = house,
            rent_node.close_in_end = True

            rent_house_root.add_child(info_action)
            rent_house_root.add_child(rent_node)

            dialog_tree.add_root(rent_house_root)

    elif house.owner:
        if house.owner.id == player.dbid:
            if house.type == 0:
                owned_root: ListNode = ListNode("owned_root", "", "Kiválaszt", "Bezár", f"{house.id} ház")

                sell_node_content: str = "{{FFFFFF}}Biztos elakarod adni a házat {{b4a2da}} " + format_numbers(int(house.price + house.house_type.price * .75)) + " {{FFFFFF}}Ft ért?"
                sell_node = ConfirmNode("sell_node", sell_node_content, "Igen", "Nem", "Ház eladás", "Eladás")
                sell_node.response_handler=sell_house
                sell_node.response_handler_parameters=house,
                
                spawn_action: ActionNode = ActionNode("set_spawn_noce", f"{'Bejelentkezés' if not house.is_spawn else 'Kijelentkezés'}")
                spawn_action.response_handler = set_spawn_house
                spawn_action.response_handler_parameters = house,
                spawn_action.close_in_end = True


                owned_root.add_child(enter_action)
                owned_root.add_child(spawn_action)
                owned_root.add_child(lock_action)
                owned_root.add_child(sell_node)

                dialog_tree.add_root(owned_root)
            else:
                rented_root: ListNode = ListNode("rented_root", "", "Kiválaszt", "Bezár", f"{house.id} ház")

                cancel_rent_node = ConfirmNode("cancel_rent_node", "{{FFFFFF}}Biztos leakarod mondai a bérlését? A bérleti díjat nem kapod vissza!", "Igen", "Nem", f"{house.id} ház", "Bérlés felmondása")
                cancel_rent_node.response_handler = cancel_rent
                cancel_rent_node.response_handler_parameters = house,

                rent_node_content: str = ("{{FFFFFF}}Hány napig szertné bérbe venni a lakást még? {{FFFFFF}}\n Ár:{{b4a2da}} " + format_numbers(house.price) + "{{FFFFFF}} Ft / nap")
                extend_rent_node: InputNode = InputNode("extend_rent_node", rent_node_content, "Hosszabítás", "Mégsem", f"{house.id} ház", display=f"Bérleti idő meghosszabítása. {format(house.price, '3_d').replace("_", " ")} Ft/nap. Bérlés vége: {house.rent_date:%Y.%m.%d}")                
                extend_rent_node.response_handler = extend_rent
                extend_rent_node.response_handler_parameters = house,
                extend_rent_node.back_after_input = True,
                
                spawn_action: ActionNode = ActionNode("set_spawn_noce", f"{'Bejelentkezés' if not house.is_spawn else 'Kijelentkezés'}")
                spawn_action.response_handler = set_spawn_house
                spawn_action.response_handler_parameters = house,
                spawn_action.close_in_end = True

                rented_root.add_child(enter_action)
                rented_root.add_child(spawn_action)
                rented_root.add_child(lock_action)
                rented_root.add_child(cancel_rent_node)
                rented_root.add_child(extend_rent_node)

                dialog_tree.add_root(rented_root)

        else:
            guest_root: ListNode = ListNode("guest_root", "", "Kiválaszt", "Bezár", f"{house.id} ház")

            guest_root.add_child(enter_action)
            guest_root.add_child(info_action)
            guest_root.add_child(crack_lock_action)

            dialog_tree.add_root(guest_root)

    dialog_tree.show_root_dialog(player)
