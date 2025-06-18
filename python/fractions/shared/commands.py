import random

from python.dialogtree import DialogTree
from python.dialogtree.dialogtree import DialogTreeNode
from python.model.server import Player
from python.utils.enums.colors import Color
from python.utils.enums.dialog_style import DialogStyle
from python.utils.helper.function import wrap_color
from .functions import change_duty, get_fraction_group_name, send_call_to_fraction
from .functions import change_duty_skin
from .functions import check_have_valid_fraction_skin
from .functions import handel_locker_stuff_action
from .functions import make_locker_content, select_new_fraction_skin, handle_new_skin
from .functions import make_locker_enable_weapons
from .functions import make_locker_stuff
from ... import TranslationKeys
from ...utils.decorator import cmd_arg_converter


@Player.command(aliases=("jelveny",))
@Player.using_registry
def badge(player: Player) -> None:
    if player.fraction is None:
        player.send_client_message(Color.RED, "(( Nem vagy egy frakció tagja se! ))")
        return

    rng = random.Random(player.dbid + 97)
    player.broadcast_system_message(Color.WHITE, "|______________J E L V É N Y_______________|", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Szervezet: {wrap_color("00C0FF", player.fraction.name)}", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Név: {{00C0FF}}{player.name}", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Rendfokozat: {{00C0FF}}{player.rank.name}", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Jelvényszám: {{00C0FF}}{rng.randint(0, 99999):0>5}", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Jelenleg {{00C0FF}}Szolgálatban" if player.in_duty else
                                                 f"Jelenleg {{00C0FF}}Nincs szolgálatban", 5.0)


@Player.command
@Player.using_registry
def beosztott(player: Player) -> None:
    pass


@Player.command
@Player.using_registry
def oltozo(player: Player) -> None:
    if player.fraction is None:
        player.send_client_message(Color.RED, "(( Nem vagy egy frakció tagja se! ))")
        return

    if not player.in_duty_point and player.fraction is not None and int(player.fraction.duty_everywhere) == 0:
        player.send_client_message(Color.RED, "(( Nem vagy a megfelelo helyen! ))")
        return

    if not check_have_valid_fraction_skin(player):
        player.send_client_message(Color.RED, "(( Nem megfelelo a szolgalati ruhad! Valasz egyet! ))")
        select_new_fraction_skin()
        return

    locker_tree: DialogTree = DialogTree()

    locker_root: DialogTreeNode = DialogTreeNode("locker_root", DialogStyle.TABLIST, "Öltöző szekrény", "",
                                                 "Kiválaszt", "Bezár",
                                                 custom_content_handler=make_locker_content)

    skin_node: DialogTreeNode = DialogTreeNode("change_skin_node", DialogStyle.TABLIST,
                                               "Öltöző szekrény - Egyenruha",
                                               "Átöltöz\nCsere", "Kiválaszt", "Vissza")

    change_skin_node: DialogTreeNode = DialogTreeNode("skin_node", DialogStyle.TABLIST, "", "", "", "",
                                                      just_action=True,
                                                      back_to_root=True,
                                                      custom_handler=change_duty_skin)

    newskin_skin_node: DialogTreeNode = DialogTreeNode("skin_node", DialogStyle.TABLIST, "", "", "", "",
                                                       just_action=True,
                                                       close_in_end=True,
                                                       custom_handler=handle_new_skin)

    stuff_node: DialogTreeNode = DialogTreeNode("stuff_node", DialogStyle.TABLIST, "Öltöző szekrény - Felszerelés",
                                                "", "Kiválaszt", "Vissza",
                                                use_same_children=True,
                                                custom_content_handler=make_locker_stuff)

    select_stuff_node: DialogTreeNode = DialogTreeNode("select_stuff_node", DialogStyle.TABLIST,
                                                       "Öltöző szekrény - Felszerelés",
                                                       "", "Kiválaszt", "Vissza",
                                                       use_same_children=True,
                                                       custom_content_handler=make_locker_enable_weapons,
                                                       custom_content_handler_node_parameters=("stuff_node.slot",))

    give_stuff_node: DialogTreeNode = DialogTreeNode("select_stuff_node", DialogStyle.TABLIST,
                                                     "", "", "", "",
                                                     just_action=True,
                                                     jump_to="stuff_node",
                                                     custom_handler=handel_locker_stuff_action,
                                                     custom_handler_node_parameters=("select_stuff_node.weapon_id",
                                                                                     "stuff_node.slot"))

    duty_node: DialogTreeNode = DialogTreeNode("duty_node", DialogStyle.TABLIST, "", "", "", "",
                                               just_action=True,
                                               back_after_input=True,
                                               custom_handler=change_duty)

    locker_root.add_child(skin_node)
    locker_root.add_child(duty_node)
    locker_root.add_child(stuff_node)

    skin_node.add_child(change_skin_node)
    skin_node.add_child(newskin_skin_node)

    stuff_node.add_child(select_stuff_node)
    select_stuff_node.add_child(give_stuff_node)

    locker_tree.add_root(locker_root)

    locker_tree.show_root_dialog(player)


@Player.command(aliases=("szolg", "szolgalat",))
@Player.using_registry
def duty(player: Player) -> None:
    if player.fraction is None:
        player.send_client_message(Color.RED, "(( Nem vagy egy frakció tagja se! ))")
        return

    if player.in_duty:
        player.send_system_message(Color.GREEN, "Befejezted a szolgálatot!")
        player.send_system_message(Color.ORANGE, "Minden fegyvert vissza raktál a szekrénybe!")
        player.fraction.duty_players.remove(player)

    else:
        player.send_system_message(Color.GREEN, "Szolgalata álltal!")
        player.send_system_message(Color.ORANGE, "Minden fegyver ami a kezedbe volt el lett törölve!")
        player.fraction.duty_players.append(player)

    player.reset_weapons()
    player.in_duty = not player.in_duty


@Player.command
@Player.using_registry
@cmd_arg_converter
def testcall(player: Player, fraction_type: int, anonymous: int, *msg):

    if fraction_type is str:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
        return

    send_call_to_fraction(fraction_type, " ".join(msg), player.get_pos(), None if anonymous else player)


@Player.command(aliases=("elfogad",))
@Player.using_registry
@cmd_arg_converter
def accept(player: Player, type: str, call_number: int):

    match type.lower():
        case "rendőr" | "rendor" | "mento" | "mentő" | "tuzolto" | "tűzoltó":
            if call_number is str:
                player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
                return

            call_data = player.fraction.calls.get(call_number, None)

            if call_data is None:
                player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.CALLNOTFOUND)
                return

            x = call_data[1][0]
            y = call_data[1][1]
            z = call_data[1][2]
            player.set_checkpoint(x, y, z, 5)

            player.fraction.send_msg(TranslationKeys.CALLACCEPTBY, player.name, call_number)
            player.send_system_message_multi_lang(Color.GREEN, TranslationKeys.CALLACCEPT, call_number)

            try:
                caller: Player | None = call_data[0]

                if caller is not None:
                    response_name: str = get_fraction_group_name(player.fraction.type)
                    caller.send_system_message_multi_lang(Color.GREEN, TranslationKeys.CALLACCEPTED, response_name, response_name)

            except Exception as e:
                return

        case _:
            player.send_system_message_multi_lang(Color.ORANGE, "Nincs ilyen típus!")
            pass
