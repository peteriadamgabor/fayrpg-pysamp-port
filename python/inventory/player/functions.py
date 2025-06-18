from sqlalchemy import select
from python.database.context_managger import transactional_session
from python.model.database import InventoryItem as InventoryItemDB
from python.model.server import Player 
from python.server.database import PLAYER_SESSION
from python.utils.enums.colors import Color
from python.utils.helper.python import try_parse_int

from python.dialogtree import DialogTree
from python.dialogtree import ListNode
from python.dialogtree import ActionNode
from python.dialogtree import InputNode


@Player.using_registry
def show_inventory(player: Player, is_search: bool = False) -> None:
    root_node: ListNode = ListNode("inventory_root", "Mennyiség\tNév\tAdat\n", "Kiválaszt", "Bezár", "Táska", True, True)

    inventory_root: DialogTree = DialogTree()
    root_node.set_tree(inventory_root)
    inventory_root.add_root(root_node)

    for inventory_item in player.items:
        metad_data = ""

        if inventory_item.inventory_item_data and inventory_item.inventory_item_data.vehicle and not is_search:
            metad_data = inventory_item.inventory_item_data.vehicle.plate
            display = f"{inventory_item.amount}\t{inventory_item.item.name}\t{metad_data}"
        else:
            display =f"{inventory_item.amount}\t{inventory_item.item.name}\t{metad_data}"
            
        node = ListNode(f"item_node", "", "Kiválaszt", "Vissza", f"{inventory_item.item.name}", display=display)

        node.set_tree(inventory_root)
        
        use_node: ActionNode = ActionNode("inventory_use", "Használ")
        use_node.response_handler = handel_item_use
        use_node.response_handler_parameters = inventory_item.id,
        use_node.close_in_end = True
        
        use_node.set_tree(inventory_root)

        player_node: InputNode = InputNode("inventory_transfer_select_player", "Add meg a játékos nevét/id -jét akinek adni akarod.\nHa a hozzád legközelebbi játékosnak akarod adni, írj '-1' -et!", "Átad", "Mégsem", "Táska - átadás", "Átad")
        player_node.save_input = True
        player_node.guard = check_is_split_item
        player_node.guard_parameters = inventory_item.id,
        player_node.guard_run_before_show = False
        player_node.guard_run_before_handler = True
        player_node.response_handler = handel_direct_transfer_item
        player_node.response_handler_parameters = inventory_item.id,
        player_node.set_tree(inventory_root)

        amount_node: InputNode = InputNode("inventory_transfer_amount", "Add meg a mennyiséget!\nTárgy: #inventory_root.name# mennyiség:#inventory_root.amount#", "Átad", "Mégsem", "Táska - átadás", "")
        amount_node.save_input = True
        amount_node.close_in_end = True
        amount_node.response_handler = handel_indirect_transfer_item
        amount_node.response_handler_parameters = inventory_item.id, 
        amount_node.response_handler_node_parameters = "inventory_transfer_select_player.input_value",
        amount_node.set_tree(inventory_root)

        drop_node: ActionNode = ActionNode("inventory_use", "Eldob")
        drop_node.response_handler = handel_item_drop
        drop_node.response_handler_parameters = inventory_item.id,
        drop_node.close_in_end = True
        drop_node.set_tree(inventory_root)

        node.add_child(use_node)
        node.add_child(player_node)
        player_node.add_child(amount_node)
        node.add_child(drop_node)

        root_node.add_child(node)
    
    inventory_root.show_root_dialog(player)


@Player.using_registry
def handel_item_use(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs) -> None:
    inv_item_id: int = int(args[0])

    with transactional_session(PLAYER_SESSION) as session:
        stmt = select(InventoryItemDB).where(InventoryItemDB.id == inv_item_id)
        inv_item: InventoryItemDB | None = session.scalars(stmt).first()

        if not inv_item or not inv_item.item:
            return None

        if inv_item.item.execute:
            eval(inv_item.item.execute)

        player.load_items()


@Player.using_registry
def item_give_hp(player: Player, inv_id: int, value: float) -> None:
    player.health += value
    player.remove_item(inv_id, 1)

@Player.using_registry
def item_give_weapon(player: Player, inv_id: int, weapon_id: int, amount: int) -> None:
    player.give_weapon(weapon_id, amount)
    player.remove_item(inv_id)

@Player.using_registry
def check_is_split_item(_: Player, *args) -> bool:
    inv_item_id: int = int(args[0])

    with transactional_session(PLAYER_SESSION) as session:
        inv_item: InventoryItemDB | None = session.scalars(select(InventoryItemDB).where(InventoryItemDB.id == inv_item_id)).first()
        return inv_item is not None and inv_item.item is not None and not inv_item.item.is_stackable


@Player.using_registry
def handel_direct_transfer_item(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs) -> None:
    target_player: Player | None = Player.fiend(input_text) if input_text != '-1' else player.get_nearest_player()

    if target_player is None:
        if input_text != '-1':
            player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        else:
            player.send_system_message(Color.ORANGE, "Nincs senki a közeledben!")
        return

    inv_item_id: int = int(args[0])
    with transactional_session(PLAYER_SESSION) as session:
        stmt = select(InventoryItemDB).where(InventoryItemDB.id == inv_item_id)
        inv_item: InventoryItemDB = session.scalars(stmt).first()
        inv_item.player_id = target_player.dbid

@Player.using_registry
def handel_indirect_transfer_item(player: Player, response: int, list_item: int, input_text: str, *args) -> bool:
    target_player: Player | None = Player.fiend(args[1]) if args[1] != '-1' else player.get_nearest_player()
    if target_player is None:
        if args[1] != '-1':
            player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        else:
            player.send_system_message(Color.ORANGE, "Nincs senki a közeledben!")
        return False

    if (transfer_amount := try_parse_int(input_text)) is None:
        player.send_client_message(Color.RED, "Számmal kell megadni!")
        return False

    inventory_item_id = int(args[0])

    if not player.have_enough_item(inventory_item_id, transfer_amount):
        player.send_system_message(Color.RED, "Nincs nálad ennyi!")
        return False

    player.transfer_item(target_player, inventory_item_id, transfer_amount)
    return True


@Player.using_registry
def handel_item_drop(player: Player, response: int, list_item: int, input_text: str, *args) -> bool:
    player.remove_item(int(args[0]))
