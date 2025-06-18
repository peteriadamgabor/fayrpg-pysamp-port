from pyeSelect.eselect import Menu, MenuItem
from python.model.server import Player, Business
from python.model.database import Business as BusinessDB
from python.model.database import Skin as SkinDB
from python.model.database import ShopItem as ShopItemDB

from python.dialogtree.dialog_tree import DialogTree
from python.dialogtree.nodes.action import ActionNode
from python.dialogtree.nodes.list import ListNode

from python.utils.enums.business_type import BusinessTypeEnum
from python.utils.enums.colors import Color
from python.utils.enums.translation_keys import TranslationKeys
from python.utils.globals import BUESSNES_VIRTUAL_WORD

from sqlalchemy import select
from python.server.database import BUSINESS_SESSION

from python.database import transactional_session
from python.utils.helper.function import get_skin_id
from python.utils.helper.python import format_numbers

from python.business.function import change_skin

@Player.command
@Player.using_registry
def ruha(player: Player):

    if player.virtual_world < BUESSNES_VIRTUAL_WORD:
        player.send_system_message_multi_lang(Color.RED, "Nem vagy ruhaboltban!")
        return

    business: Business | None = Business.get_registry_item(player.virtual_world - BUESSNES_VIRTUAL_WORD)

    if not business or not business.business_type:
        return

    if business.business_type.id != BusinessTypeEnum.CLOTHSHOP:
        player.send_system_message_multi_lang(Color.RED, "Nem vagy ruhaboltban!")
        return

    with transactional_session(BUSINESS_SESSION) as session:
        skins: list[SkinDB] = session.query(BusinessDB).filter(BusinessDB.id == business.id).one().skins
        menu = Menu(
            f'{business.name}',
            [MenuItem(get_skin_id(skin.id), str(format_numbers(skin.price)) + " Ft") for skin in skins if skin.sex == player.sex],
            on_select=change_skin,
        )
        menu.show(player)


@Player.command
@Player.using_registry
def vasarol(player: Player):

    if player.virtual_world < BUESSNES_VIRTUAL_WORD:
        player.send_system_message_multi_lang(Color.RED, "Nem vagy boltban!")
        return

    business: Business | None = Business.get_registry_item(player.virtual_world - BUESSNES_VIRTUAL_WORD)

    if not business or not business.business_type:
        return

    if business.business_type.id != BusinessTypeEnum.STORE:
        player.send_system_message_multi_lang(Color.RED, "Nem vagy boltban!")
        return

    with transactional_session(BUSINESS_SESSION) as session:
        shop_items: list[ShopItemDB] = session.query(BusinessDB).filter(BusinessDB.id == business.id).one().items

        if len(shop_items) == 0:
            return

        root_node: ListNode = ListNode("root", "Termék\tMennyiség\tÁr", "Kiválaszt", "Bezár", f"{business.name} árukészlete", True, True)
        tree: DialogTree = DialogTree()
        root_node.set_tree(tree)
        tree.add_root(root_node)

        for shop_item in shop_items:
            menu_node: ActionNode = ActionNode("node", f"{shop_item.item.name}\t{shop_item.amount}\t{format_numbers(shop_item.price)} Ft")
            menu_node.response_handler = buy_item
            menu_node.response_handler_parameters = (business.id, shop_item.item_id)
            menu_node.close_in_end = True

            root_node.add_child(menu_node)

    tree.show_root_dialog(player)

@Player.using_registry
def buy_item(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs) -> None:
    business_id: int = args[0]
    item_id: int = args[1]

    with transactional_session(BUSINESS_SESSION) as session:
        shop_item: ShopItemDB = session.query(ShopItemDB).filter((ShopItemDB.item_id == item_id) & (ShopItemDB.business_id == business_id)).one()

        if shop_item.amount <= 0:
            player.send_system_message_multi_lang(Color.ORANGE, "A termék elfogyott!")
            return

        if not player.transfer_money(shop_item.price):
            player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTENOUGHMONEY)
            return

        shop_item.amount -= 1
        player.give_item(item_id, shop_item.give_amount)
        player.send_system_message_multi_lang(Color.GREEN, f"Vásároltál {shop_item.give_amount} darab {shop_item.item.name} {shop_item.price} Ft ért")
