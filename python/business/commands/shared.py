from python.business.function import change_business_interior
from python.dialogtree.dialog_tree import DialogTree
from python.dialogtree.nodes.action import ActionNode
from python.dialogtree.nodes.confim import ConfirmNode
from python.dialogtree.nodes.list import ListNode
from python.model.server import Player, Business
from python.model.database import Business as BusinessDB
from python.model.database import Interior as InteriorDB
from python.model.database import BusinessType as BusinessTypeDB
from python.model.database import Player as PlayerDB


from sqlalchemy import select
from python.server.database import BUSINESS_SESSION

from python.database import transactional_session
from python.utils.helper.python import format_numbers

@Player.command
@Player.using_registry
def ceg(player: Player):
    with transactional_session(BUSINESS_SESSION) as session:
        db_businesses: list[BusinessDB] = list(session.scalars( select(BusinessDB).join(PlayerDB).where(BusinessDB.owner_id == player.dbid)).all())

        root_node: ListNode = ListNode("bizz_root", "", "Kiválaszt", "Bezár", "Cégek")
        tree: DialogTree = DialogTree()
        root_node.set_tree(tree)
        tree.add_root(root_node)

        for db_business in db_businesses:
            business: Business | None = Business.get_registry_item(db_business.id)

            if not business:
                continue

            bizz_node: ListNode = ListNode("bizz_node", "", "Kiválaszt", "Bezár", f"{business.name} adatai", False, False, business.name)
            price_node: ActionNode = ActionNode("price_node", f"Piaci ár: {format_numbers(business.price)} Ft")
            interior_node: ListNode = ListNode("interior_node", "", "Kiválaszt", "Bezár", f"{business.name} belső átalakítás", False, False, f"Belső: {business.interior.name if business.interior else "Nincs kiválasztva"}")

            db_interiors: list[InteriorDB] = list(session.scalars(
                select(InteriorDB).join(BusinessTypeDB).where(BusinessTypeDB.id == db_business.business_type_id)).all())

            for interior in db_interiors:
                new_interior_node: ConfirmNode = ConfirmNode("new_interior_node", f"Biztos meg szeretnéd venni ezt a belsőt {format_numbers(interior.price)} Ft-ért?", "Kiválaszt", "Mégsem", "Belső megváltoztatás", f"{interior.name} - {format_numbers(interior.price)} Ft")
                new_interior_node.response_handler = change_business_interior
                new_interior_node.response_handler_parameters = (business.id,  interior.id) 
                interior_node.add_child(new_interior_node)

            bizz_node.add_child(price_node)
            bizz_node.add_child(interior_node)

            root_node.add_child(bizz_node)

    tree.show_root_dialog(player)