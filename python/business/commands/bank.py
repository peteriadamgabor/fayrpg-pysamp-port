from python.utils.globals import BUESSNES_VIRTUAL_WORD
from ..functions.bank import deposit_handler
from ..functions.bank import deposit_bank_validator
from ..functions.bank import list_player_bank_accounts
from ..functions.bank import create_new_bank_account 
from ..functions.bank import check_bank_password
from ..functions.bank import withdrawal_handler
from ..functions.bank import change_password_bank_account
from ..functions.bank import bank_info_content_handler

from python.dialogtree.dialogtree import DialogTreeNode
from python.dialogtree import DialogTree

from python.model.server import Player, Business

from python.utils.enums.business_type import BusinessTypeEnum
from python.utils.enums.colors import Color
from python.utils.enums.dialog_style import DialogStyle


@Player.command
@Player.using_registry
def bank(player: Player):
    business: Business = Business.get_registry_item(player.get_virtual_world() - BUESSNES_VIRTUAL_WORD)

    if business is None or business.business_type_id != BusinessTypeEnum.BANK:
        player.send_client_message(Color.RED, "(( Nem vagy bankban! ))")
        return

    root_title = f"{business.name} - Válassz opciót!"
    root_content = "Pénz befizetés\nBankszámla műveletek\nFizetási számlaszám megadása"

    bank_root = DialogTreeNode("bank_root", DialogStyle.LIST, root_title, root_content,
                               "Kiválaszt", "Bezár")

    # region Pénz befizetés

    deposit_bank_title = f"Pénz befizetés"
    deposit_bank_content = " Kérem adja meg a bankszámlaszámot, amire befizetni szeretne!"

    deposit_bank = DialogTreeNode("deposit_bank", DialogStyle.INPUT, deposit_bank_title, deposit_bank_content,
                                  "Tovább", "Vissza",
                                  save_input=True,
                                  custom_handler=deposit_bank_validator)

    deposit_amount_title = f"Pénz befizetés"
    deposit_amount_content = " Kérem adja meg a befizetni kívánt összeget!"

    deposit_amount = DialogTreeNode("deposit_amount", DialogStyle.INPUT, deposit_amount_title, deposit_amount_content,
                                    "Befizetés", "Mégsem",
                                    save_input=True,
                                    back_to_root=True,
                                    custom_handler=deposit_handler,
                                    custom_handler_node_parameters=("deposit_bank.input_value",))

    deposit_bank.add_child(deposit_amount)

    # endregion

    # region Bankszámla műveletek

    operations_title = f"Bankszámla műveletek"
    operations_content = "Saját számlák\nBelépés számlaszámmal\nBankszámla létrehozása\nElfelejtett jelszó"

    operations_root = DialogTreeNode("operations_root", DialogStyle.LIST, operations_title, operations_content,
                                     "Kiválaszt", "Mégsem")

    owned_title = "Saját számlák"
    owned_content = ""

    owned_list = DialogTreeNode("owned_list", DialogStyle.LIST, owned_title, owned_content,
                                "Kiválaszt", "Vissza",
                                custom_content_handler=list_player_bank_accounts,
                                use_same_children=True)

    enter_bank_title = "Belépés számlaszámmal"
    enter_bank_content = "Kérem adja meg a bankszámlaszámot, amire be akar lépni!"

    enter_bank = DialogTreeNode("enter_bank", DialogStyle.INPUT, enter_bank_title, enter_bank_content,
                                "Tovább", "Vissza")

    enter_bank_password_content = "Kérem adja meg a bankszámla jelszavát!"

    enter_bank_password = DialogTreeNode("enter_bank", DialogStyle.INPUT, enter_bank_title, enter_bank_password_content,
                                         "Belépés", "Vissza")

    enter_own_bank_password = DialogTreeNode("enter_bank", DialogStyle.INPUT, enter_bank_title,
                                             enter_bank_password_content,
                                             "Belépés", "Vissza",
                                             custom_handler=check_bank_password,
                                             custom_handler_node_parameters=("owned_list.id",))

    operations_title = "Bankszámla műveletek"
    operations_content = ("Pénz befizetés\nPénz felvétel\nPénz utalás"
                          "\nJelszóváltoztatás\nSzámlainformáció\nSzámlatörténet")

    operations = DialogTreeNode("owned_operations", DialogStyle.LIST, operations_title, operations_content,
                                "Kiválaszt", "Vissza",
                                back_to_root=True)

    deposit_title = f"Bankszámla műveletek - Pénz befizetés"
    deposit_content = " Kérem adja meg a befizetni kívánt összeget!"

    deposit = DialogTreeNode("deposit", DialogStyle.INPUT, deposit_title, deposit_content,
                             "Befizetés", "Mégsem",
                             back_after_input=True,
                             custom_handler=deposit_handler,
                             custom_handler_node_parameters=("owned_list.id", "enter_bank.input",))

    withdrawal_title = f"Bankszámla műveletek - Pénz felvétel"
    withdrawal_content = f"Kérem adja meg az összeget, amelyet fel akar venni!"

    withdrawal = DialogTreeNode("withdrawal", DialogStyle.INPUT, withdrawal_title, withdrawal_content,
                                "Kivesz", "Mégsem",
                                back_after_input=True,
                                custom_handler=withdrawal_handler,
                                custom_handler_node_parameters=("owned_list.id", "enter_bank.input",))

    new_password_title = f"Bankszámla műveletek - Jelszóváltoztatás"
    new_password_content = f"Kérem adja meg az új jelszót!"

    new_password = DialogTreeNode("new_password", DialogStyle.INPUT, new_password_title, new_password_content,
                                  "Mentés", "Mégsem",
                                  back_after_input=True,
                                  custom_handler=change_password_bank_account,
                                  custom_handler_node_parameters=("owned_list.id", "enter_bank.input",))

    bank_info_title = f"Bankszámla műveletek - Számlainformáció"
    bank_info_content = f""

    bank_info = DialogTreeNode("bank_info", DialogStyle.MSGBOX, bank_info_title, bank_info_content,
                               "Vissza", "",
                               stay_if_none=False,
                               custom_content_handler=bank_info_content_handler,
                               custom_content_handler_node_parameters=("owned_list.id", "enter_bank.input",))

    create_title = "Bankszámla létrehozása"
    create_content = "Addja meg a bankszámlája jelszavát!"

    create_input = DialogTreeNode("create_input", DialogStyle.INPUT, create_title, create_content,
                                  "Létrehozás", "Mégsem",
                                  custom_handler=create_new_bank_account,
                                  stay_if_none=False)

    enter_bank.add_child(enter_bank_password)

    owned_list.add_child(enter_own_bank_password)

    operations.add_child(deposit)
    operations.add_child(withdrawal)
    operations.add_child(None)
    operations.add_child(new_password)
    operations.add_child(bank_info)

    enter_own_bank_password.add_child(operations)

    operations_root.add_child(owned_list)
    operations_root.add_child(enter_bank)
    operations_root.add_child(create_input)

    # endregion Bankszámla műveletek

    bank_root.add_child(deposit_bank)
    bank_root.add_child(operations_root)

    dialog_tree: DialogTree = DialogTree()
    dialog_tree.add_root(bank_root)

    dialog_tree.show_root_dialog(player)
