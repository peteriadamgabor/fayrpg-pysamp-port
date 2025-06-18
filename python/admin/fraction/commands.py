from python.dialogtree import DialogTree
from python.dialogtree.dialogtree import DialogTreeNode
from python.model.server import Player
from python.utils.enums.colors import Color
from python.utils.enums.dialog_style import DialogStyle
from .functions import list_fractions, list_fraction_parameter, change_fraction_name, change_fraction_acronym, \
    list_fraction_players, save_fraction_new_rank, list_fraction_ranks, list_player_data, list_ranks_for_promot, \
    list_possible_divisions, promote_player, change_player_deivison
from ..functions import check_player_role_permission

from python.model.dto import Fraction as FractionDTO


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def listfractions(player: Player):
    fraction_list_root_node: DialogTreeNode = DialogTreeNode("root_node", DialogStyle.LIST, "Frakciók",
                                                             "", "Kiválaszt", "Bezár",
                                                             custom_content_handler=list_fractions)

    fraction_data: DialogTreeNode = DialogTreeNode("fraction_data_node", DialogStyle.TABLIST,
                                                   "Frakció - #root_node.name#",
                                                   "", "Kiválaszt", "Vissza",
                                                   custom_content_handler=list_fraction_parameter,
                                                   custom_content_handler_node_parameters=("root_node.id",))

    change_name: DialogTreeNode = DialogTreeNode("change_name_node_action", DialogStyle.INPUT,
                                                 "Frakció - Név átírás",
                                                 "Add meg a frakció új nevét!", "Elküld", "Vissza",
                                                 back_to_root=True,
                                                 custom_handler=change_fraction_name,
                                                 custom_handler_node_parameters=("root_node.id",))

    change_acronym: DialogTreeNode = DialogTreeNode("change_acronym_action", DialogStyle.INPUT,
                                                    "Frakció - Név átírás",
                                                    "Add meg a frakció új nevét!", "Elküld", "Vissza",
                                                    back_after_input=True,
                                                    custom_handler=change_fraction_acronym,
                                                    custom_handler_node_parameters=("root_node.id",))

    list_divisions: DialogTreeNode = DialogTreeNode("list_divisions_node", DialogStyle.INPUT,
                                                    "Frakció - Alosztályok",
                                                    "", "Elküld", "Vissza",
                                                    just_action=True,
                                                    custom_content_handler=None,
                                                    custom_content_handler_node_parameters=("root_node.id",))

    list_ranks: DialogTreeNode = DialogTreeNode("list_ranks_node", DialogStyle.LIST,
                                                "Frakció - Rangok",
                                                "Új hozzá adása\n", "Kiválaszt", "Vissza",
                                                fixed_first_chiled=True,
                                                use_same_children=True,
                                                custom_content_handler=list_fraction_ranks,
                                                custom_content_handler_node_parameters=("root_node.id",))

    # region new_rank

    new_rank: DialogTreeNode = DialogTreeNode("new_rank_node", DialogStyle.TABLIST,
                                              "Frakció - Új rang létrehozása",
                                              "Sorszám\t#new_rank_order_action.input_value#\n"
                                              "Név\t#new_rank_name_action.input_value#\n"
                                              "Mentés",
                                              "Kiválaszt", "Vissza")

    new_rank_order: DialogTreeNode = DialogTreeNode("new_rank_order_action", DialogStyle.INPUT,
                                                    "Frakció - Új rang név",
                                                    "Add meg a rang új sorszámát!", "Mentés", "Vissza",
                                                    save_input=True,
                                                    back_after_input=True)

    new_rank_name: DialogTreeNode = DialogTreeNode("new_rank_name_action", DialogStyle.INPUT,
                                                   "Frakció - Új rang név",
                                                   "Add meg a rang új nevét!", "Mentés", "Vissza",
                                                   save_input=True,
                                                   back_after_input=True)

    new_rank_save: DialogTreeNode = DialogTreeNode("new_rank_save_action", DialogStyle.INPUT,
                                                   "Frakció - Új rang név",
                                                   "Add meg a rang új nevét!", "Mentés", "Vissza",
                                                   just_action=True,
                                                   back_to_root=True,
                                                   custom_handler=save_fraction_new_rank,
                                                   custom_handler_node_parameters=("new_rank_order_action.input_value",
                                                                                   "new_rank_name_action.input_value",
                                                                                   "root_node.id")
                                                   )

    # endregion new_rank

    rank_data: DialogTreeNode = DialogTreeNode("rank_data_node", DialogStyle.LIST,
                                               "Frakció - Rank adatok",
                                               "Order\nNév", "Mentés", "Vissza",
                                               back_to_root=True)

    list_players: DialogTreeNode = DialogTreeNode("list_players_node", DialogStyle.TABLIST,
                                                  "Frakció - Tagok",
                                                  "", "Elküld", "Vissza",
                                                  use_same_children=True,
                                                  custom_content_handler=list_fraction_players,
                                                  custom_content_handler_node_parameters=("root_node.id",))

    player_data: DialogTreeNode = DialogTreeNode("player_data_node", DialogStyle.TABLIST,
                                                 "Frakció - #list_players_node.name#",
                                                 "", "Elküld", "Vissza",
                                                 custom_content_handler=list_player_data,
                                                 custom_content_handler_node_parameters=("list_players_node.id",))

    player_promote_list: DialogTreeNode = DialogTreeNode("player_promote_list_node", DialogStyle.TABLIST,
                                                         "Frakció - Rangok",
                                                         "", "Kiválaszt", "Vissza",
                                                         use_same_children=True,
                                                         custom_content_handler=list_ranks_for_promot,
                                                         custom_content_handler_node_parameters=(
                                                             "list_players_node.id",))

    player_promote: DialogTreeNode = DialogTreeNode("player_promote_action", DialogStyle.TABLIST,
                                                    "Frakció - #list_players_node.name# rang módosítás",
                                                    "", "Kiválaszt", "Vissza",
                                                    just_action=True,
                                                    use_same_children=True,
                                                    jump_to="player_data_node",
                                                    custom_handler=promote_player,
                                                    custom_handler_node_parameters=("list_players_node.id",
                                                                                    "player_promote_list_node.id"))

    player_division_list: DialogTreeNode = DialogTreeNode("player_division_list_node", DialogStyle.TABLIST,
                                                          "Frakció - Alosztáy módosítás",
                                                          "", "Kiválaszt", "Vissza",
                                                          use_same_children=True,
                                                          custom_content_handler=list_possible_divisions,
                                                          custom_content_handler_node_parameters=(
                                                              "list_players_node.id",))

    player_division_change: DialogTreeNode = DialogTreeNode("player_division_change_action", DialogStyle.TABLIST,
                                                            "-",
                                                            "", "Kiválaszt", "Vissza",
                                                            just_action=True,
                                                            use_same_children=True,
                                                            jump_to="player_data_node",
                                                            custom_handler=change_player_deivison,
                                                            custom_handler_node_parameters=("list_players_node.id",
                                                                                            "player_division_list_node.id"))

    fraction_list_root_node.add_child(fraction_data)

    fraction_data.add_child(change_name)
    fraction_data.add_child(change_acronym)
    fraction_data.add_child(list_divisions)
    fraction_data.add_child(list_ranks)
    fraction_data.add_child(list_players)

    list_players.add_child(player_data)

    player_data.add_child(player_promote_list)
    player_data.add_child(player_division_list)

    player_promote_list.add_child(player_promote)
    player_division_list.add_child(player_division_change)

    list_ranks.add_child(new_rank)
    list_ranks.add_child(rank_data)

    new_rank.add_child(new_rank_order)
    new_rank.add_child(new_rank_name)
    new_rank.add_child(new_rank_save)

    tree: DialogTree = DialogTree()
    tree.add_root(fraction_list_root_node)
    tree.show_root_dialog(player)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def setfraction(player: Player, target: int | str, fraction_id: int):
    fraction: FractionDTO | None = FractionDTO.get_registry_item(int(fraction_id))

    target_player: Player | None = Player.fiend(target)

    if not target_player:
        player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        return

    if not fraction:
        player.send_system_message(Color.ORANGE, "Nincs ilyen frakció!")
        return

    target_player.fraction = fraction
    target_player.rank = fraction.ranks[0]

    target_player.send_client_message(Color.GREEN, f"{player.role.name} {player.name} a(z) {fraction.name} frakcióba helyezett!\nA {fraction.ranks[0].name}-re/ra!")
