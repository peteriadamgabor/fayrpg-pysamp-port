import datetime

from sqlalchemy import and_, select

from pyeSelect.eselect import Menu, MenuItem
from pysamp import set_world_time
from python import exception_logger
from python.admin.player.functions import delete_fine_handler
from python.database.context_managger import transactional_session

from python.dialogtree import DialogTree
from python.dialogtree import ActionNode
from python.dialogtree import ListNode
from python.model.database import Skin as SkinDB
from python.model.database import FineType as FineTypeDB
from python.model.database import PlayerFine as PlayerFineDB
from python.model.database import Interior as InteriorDB

from python.model.server import Player, Vehicle
from python.server.database import MAIN_SESSION
from python.utils.decorator import cmd_arg_converter
from python.utils.enums.colors import Color
from python.utils.enums.states import State
from python.utils.enums.translation_keys import TranslationKeys
from python.utils.helper.item import get_item_name, is_valid_item_id
from python.utils.helper.python import try_parse_int, format_numbers, try_parse_float
from ..functions import check_player_role_permission, send_admin_action, change_skin, send_admin_action_multi_lang


@Player.command(args_name=("id/név", "összeg"), requires=[check_player_role_permission])
@Player.using_registry
@cmd_arg_converter
def givemoney(player: Player, target: str | int, value: int, *reason) -> None:
    target_player: Player | None = Player.fiend(target)

    if target_player is None:
        player.send_system_message(Color.WHITE, "Nincs ilyen játékos!")
        return

    target_player.money += value

    send_admin_action(player, f"{format_numbers(value)} Ft-ot adott {target_player.name}")

    player.send_system_message(Color.GREEN, f"Sikeresen adtál {format_numbers(value)} Ft-ot adott {target_player.name}")
    target_player.send_system_message(Color.GREEN, f"Egy admintól kaptál {format_numbers(value)} Ft-ot!")


@Player.command(args_name=("id/név",), requires=[check_player_role_permission])
@Player.using_registry
@cmd_arg_converter
def goto(player: Player, target: str | int, seat: int = 1):
    target_player: Player | None = Player.fiend(target)

    if target_player is None:
        player.send_system_message(Color.WHITE, "Nincs ilyen játékos!")
        return

    if seat is str:
        return

    player.set_back_pos()

    player.interior = target_player.interior
    player.virtual_world = target_player.virtual_world

    (x, y) = target_player.get_x_y_in_front_of(2)
    (_, _, z) = target_player.get_pos()
    angle = target_player.get_facing_angle()

    if player.in_vehicle() and player.get_state() == State.DRIVER:
        veh: Vehicle = player.get_vehicle()

        veh.set_position(x, y, z + 2)
        player.send_system_message(Color.GREEN,
                                   f"{target_player.name}[{target_player.id}]-hez lettél teleportálva!")
        return

    elif target_player.in_vehicle():
        player.put_in_vehicle(target_player.get_vehicle_id(), seat)
        player.send_system_message(Color.GREEN,
                                   f"{target_player.name}[{target_player.id}] járművébe lettél teleportálva!")
        return

    else:
        if angle < 0.0:
            angle = angle + 180.0

        if angle > 0.0:
            angle = angle - 180.0

        player.set_pos(x, y, z)
        player.set_facing_angle(angle)
        player.send_system_message(Color.GREEN, f"{target_player.name}[{target_player.id}]-hez lettél teleportálva!")
        return


@Player.command(args_name=("id/név",), requires=[check_player_role_permission])
@Player.using_registry
def gethere(player: Player, target: str | int, seat: int = 1):
    target_player: Player | None = Player.fiend(target)

    if target_player is None:
        player.send_system_message(Color.WHITE, "Nincs ilyen játékos!")
        return

    target_player.interior = player.interior
    target_player.virtual_world = player.virtual_world

    (x, y) = player.get_x_y_in_front_of(2)
    (_, _, z) = player.get_pos()
    angle = player.get_facing_angle()

    if player.in_vehicle() and player.get_state() == State.DRIVER:
        target_player.put_in_vehicle(player.get_vehicle_id(), seat)
        player.send_system_message(Color.GREEN,
                                   f"{target_player.name}[{target_player.id}] járművedbe lett teleportálva!")
        target_player.send_system_message(Color.GREEN, f"Teleportálva lettél!")
        return

    elif target_player.in_vehicle():
        veh: Vehicle = target_player.get_vehicle()

        veh.set_position(x, y, z + 2)
        player.send_system_message(Color.GREEN,
                                   f"{target_player.name}[{target_player.id}] járműve teleportálva lett!")
        target_player.send_system_message(Color.GREEN, f"Teleportálva lettél!")
        return

    else:
        if angle < 0.0:
            angle = angle + 180.0

        if angle > 0.0:
            angle = angle - 180.0

        target_player.set_pos(x, y, z)
        target_player.set_facing_angle(angle)

        target_player.send_system_message(Color.GREEN, f"Teleportálva lettél!")
        player.send_system_message(Color.GREEN,
                                   f"{target_player.name}[{target_player.id}]-hez lettél teleportálva!")
        return


@Player.command(args_name=("id/név", "skinid"), requires=[check_player_role_permission])
@Player.using_registry
def setskin(player: Player, target: str | int, value: int):
    target_player: Player | None = Player.fiend(target)

    if target_player is None:
        player.send_system_message(Color.RED, "Nincs ilyen játékos!")
        return

    c_value: int | None = try_parse_int(value)

    if c_value is None:
        player.send_system_message(Color.RED, "Számmal kell megadni!")
        return

    with MAIN_SESSION() as session:
        skin: SkinDB | None = session.query(SkinDB).filter(SkinDB.id == c_value).first()

        if skin is None:
            player.send_system_message(Color.RED, "Nincs ilyen skin!")
            return

        if skin.sex != player.sex:
            player.send_system_message(Color.RED, f"Nem adhatsz {'noi' if skin.sex else 'fefi'} "
                                                  f"skint egy {'no' if player.sex else 'fefi'}re!")
            return

        target_player.change_skin(skin.id)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def listskins(player: Player):
    with MAIN_SESSION() as session:
        skins = session.query(SkinDB).filter(and_(SkinDB.sex == bool(player.sex), SkinDB.id != 74)).order_by(
            SkinDB.id).all()
        menu = Menu(
            'Ruhák',
            [MenuItem(skin.id, str(skin.price) + " Ft") for skin in skins],
            on_select=change_skin,
        )
        menu.show(player)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def gotopos(player: Player, x: float, y: float, z: float, interior=0, vw=0):
    player.set_back_pos()

    if player.is_in_any_vehicle():
        player.get_vehicle().set_position(float(x), float(y), float(z))
        player.get_vehicle().set_virtual_world(int(vw))
        player.get_vehicle().link_to_interior(int(interior))
    else:
        player.set_pos(float(x), float(y), float(z))
        player.set_interior(int(interior))
        player.set_virtual_world(int(vw))


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def back(player: Player):
    player.back()


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def getpos(player: Player):
    x, y, z = player.get_pos()
    a: float = player.get_facing_angle()
    i: int = player.get_interior()
    w: int = player.get_virtual_world()

    player.send_system_message(Color.WHITE,
                               f"X >> {x: .4f} | Y >> {y: .4f} | Z >> {z: .4f} | A >> {a: .4f} | Interior: {i} | VirtualWord: {w}")


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def savepos(player: Player, point_name: str, *args):
    x, y, z = player.get_pos()
    a: float = player.get_facing_angle()
    i: int = player.get_interior()
    w: int = player.get_virtual_world()
    name: str = " ".join([point_name, *args])

    with open(f"scriptfiles/points/savepos.txt", "a+") as f:
        f.write(
            f"[{datetime.datetime.now()}] {player.get_name()} | name: {name} | X >> {x: .4f} | Y >> {y: .4f} | Z >> {z: .4f} | A >> {a: .4f} | Interior: {i} | VirtualWord: {w}\n")

    player.send_system_message(Color.GREEN, f"Sikeresen lementetted a {name} pontot")


@Player.command(args_name=("id/név",), requires=[check_player_role_permission])
@Player.using_registry
def asegit(player: Player, target: str | int):
    target_player: Player | None = Player.fiend(target)

    if target_player is None:
        player.send_system_message(Color.WHITE, "Nincs ilyen játékos!")
        return

    target_player.set_drunk_level(0)
    target_player.apply_animation("PED", "getup_front", 4.0, False, False, False, False, 0, True)

    player.send_system_message(Color.GREEN, "Játékos sikeresen felsegítve!")
    target_player.send_system_message(Color.GREEN, "Egy admin felsegített!")
    send_admin_action(player, f"felseígtette {target_player.name}!")


@Player.command(args_name=("id/név", "item id", "mennyiség"), requires=[check_player_role_permission])
@Player.using_registry
@exception_logger.catch
def giveitem(player: Player, target: str | int, item_id: int, amount: int, *args):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message(Color.RED, "Nincs ilyen játékos!")
        return

    if (item_id := try_parse_int(item_id)) is None and not is_valid_item_id(item_id):
        player.send_system_message(Color.RED, "Nincs ilyen item!")
        return

    if (transfer_amount := try_parse_int(amount)) is None:
        player.send_system_message(Color.RED, "Számmal kell megadni!")
        return

    if transfer_amount < 0:
        player.send_system_message(Color.RED, "Negatív szám nem lehet!")
        return

    target_player.give_item(item_id, transfer_amount)
    player.send_system_message(Color.GREEN,
                               f"Sikersen adtál {target_player.name}-nak/nek {amount} darab {get_item_name(item_id)}-t")
    send_admin_action(player, f"adott {target_player.name}-nak/nek {amount} darab {get_item_name(item_id)}-t")


@Player.command(args_name=("id/név vagy me", "hp"), requires=[check_player_role_permission])
@Player.using_registry
def sethp(player: Player, target: str | int, health: float = 100.0):
    if target != "me" and (target_player := Player.fiend(target)) is None:
        player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        return

    if (hp := try_parse_float(health)) is None:
        player.send_system_message(Color.ORANGE, "Számmal kell megadni!")

    if target == "me" or target_player.id == player.id:
        player.set_health(hp)
        player.send_system_message(Color.GREEN, f"Sikersen beálítottad az életed {hp}%-ra")
        send_admin_action(player, f"beálíltotta a saját életét {hp}%-ra")

    else:
        target_player.set_health(hp)
        player.send_system_message(Color.GREEN, f"Sikersen beálítottad {target_player.name} életét {hp}%-ra")
        send_admin_action(player, f"beálíltotta {target_player.name} életét {hp}%-ra")


@Player.command(args_name=("id/név", "interior"), requires=[check_player_role_permission])
@Player.using_registry
def setint(player: Player, target: str | int, inter: int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        return

    if (interior := try_parse_int(inter)) is None:
        player.send_system_message(Color.ORANGE, "Számmal kell megadni!")

    target_player.set_interior(interior)
    target_player.send_system_message(Color.GREEN, f"Meváltoztatták az interiorod {interior}-ra!")
    player.send_system_message(Color.GREEN, f"Sikersen beálítottad {target_player.name} interiotját {interior}-ra")
    send_admin_action(player, f"beálíltotta {target_player.name} interiotját {interior}-ra")


@Player.command(args_name=("id/név", "interior"), requires=[check_player_role_permission])
@Player.using_registry
def setvw(player: Player, target: str | int, vw_raw: int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        return

    if (vw := try_parse_int(vw_raw)) is None:
        player.send_system_message(Color.ORANGE, "Számmal kell megadni!")

    target_player.set_virtual_world(vw)
    target_player.send_system_message(Color.GREEN, f"Meváltoztatták az virtualwordöd {vw}-ra!")
    player.send_system_message(Color.GREEN, f"Sikersen beálítottad {target_player.name} virtwordjét {vw}-ra")
    send_admin_action(player, f"beálíltotta {target_player.name} virtwordjét {vw}-ra")


@Player.command(args_name=("id/név"), requires=[check_player_role_permission])
@Player.using_registry
def freeze(player: Player, target: str | int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        return

    target_player.toggle_controllable(False)
    player.send_system_message(Color.GREEN, f"Sikersen lefagyasztottad {target_player.name}")
    target_player.send_system_message(Color.GREEN, f"Lefagyasztottak!")
    send_admin_action(player, f"lefagyasztotta {target_player.name}!")


@Player.command(args_name=("id/név",), requires=[check_player_role_permission])
@Player.using_registry
def unfreeze(player: Player, target: str | int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message(Color.ORANGE, "Nincs ilyen játékos!")
        return

    target_player.toggle_controllable(True)
    player.send_system_message(Color.GREEN, f"Sikersen feloldottad {target_player.name}")
    target_player.send_system_message(Color.GREEN, f"Feloldottak!")
    send_admin_action(player, f"feloldotta {target_player.name}!")


@Player.command(aliases=('nokorhaz',), args_name=("id/név",), requires=[check_player_role_permission])
@Player.using_registry
def releashospital(player: Player, target: str | int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTAPLAYER)
        return

    if not target_player.have_hospital_time:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTINHOSPITAL)
        return

    with transactional_session(MAIN_SESSION) as session:
        last_hospital_fine: PlayerFineDB = session.scalars(select(PlayerFineDB)
                                                           .join(PlayerFineDB.fine_type)
                                                           .where(
            (PlayerFineDB.player_id == target_player.dbid) & (PlayerFineDB.is_payed == False) & (
                        FineTypeDB.code == "HF"))
                                                           .order_by(PlayerFineDB.issued.desc())).first()

        last_hospital_fine.is_payed = True
        last_hospital_fine.payed_amount = last_hospital_fine.amount

        target_player.hospital_time = 0
        target_player.hospital_release_date = datetime.datetime.now()

        player.send_system_message_multi_lang(Color.GREEN, TranslationKeys.ADMINREALESHOSPITAL, target_player.name)
        target_player.send_system_message_multi_lang(Color.GREEN, TranslationKeys.REALESHOSPITAL, player.name,
                                                     format_numbers(last_hospital_fine.amount))

        send_admin_action_multi_lang(player, TranslationKeys.ACMDREALESHOSPITAL, True, target_player.name)


@Player.command(args_name=("nyelv",))
@Player.using_registry
def lang(player: Player, language: str):
    player.language = language.lower()
    player.send_system_message_multi_lang(Color.GREEN, TranslationKeys.CHNAGELANG, language)


@Player.command
@Player.using_registry
def test(player: Player, amount: int):
    player.set_money(int(amount))


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def setplayerlvl(player: Player, target: str | int, lvl: int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTAPLAYER)
        return

    if (setlvl := try_parse_int(lvl)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
        return

    target_player.lvl = setlvl
    send_admin_action_multi_lang(player, "SETLVLACMD", True, target_player.name)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def refreshplayerlvl(player: Player, target: str | int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTAPLAYER)
        return

    target_player.lvl = target_player.calculate_lvl(int((target_player.played_time + 1) / 3600))
    send_admin_action_multi_lang(player, "SETLVLACMD", True, target_player.name)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def setdrunklvl(player: Player, target: str | int, value: int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTAPLAYER)
        return

    target_player.lvl = target_player.set_drunk_level(int(value))


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def giveweapon(player: Player, target: str | int, weapin_id: int, ammo: int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTAPLAYER)
        return

    if (weapinid := try_parse_int(weapin_id)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
        return

    if (amount := try_parse_int(ammo)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
        return

    if amount > 0:
        target_player.give_weapon(weapinid, amount)
    else:
        target_player.remove_weapon(weapinid)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def respawn(player: Player, target: str | int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTAPLAYER)
        return

    target_player.toggle_spectating(True)
    target_player.toggle_spectating(False)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def atartozas(player: Player, target: str | int):
    if (target_player := Player.fiend(target)) is None:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTAPLAYER)
        return

    with transactional_session(MAIN_SESSION) as session:
        player_fines: list[PlayerFineDB] = list(session.scalars(select(PlayerFineDB).where(
            (PlayerFineDB.player_id == target_player.dbid) & (PlayerFineDB.is_payed == False))).all())
        dialog_tree: DialogTree = DialogTree()

        fine_list_node: ListNode = ListNode("fine_list_node", "Indok\tDátum\tÖsszeg\n", "Megtekint", "Bezár",
                                            f"{target_player.name} tartozásai | SUM: {format_numbers(sum((i.amount - i.payed_amount) for i in player_fines))}",
                                            True, True)

        for fine in player_fines:
            fine_node: ListNode = ListNode("fine_node", "", "Kiválaszt", "Vissza", "Tartozás szerkeztő", False, False,
                                           f"{fine.reason}\t{fine.issued:%Y.%m.%d}\t{format_numbers((fine.amount - fine.payed_amount))} Ft")
            fine_list_node.add_child(fine_node)

            issuer_node: ActionNode = ActionNode("issuer_node",
                                                 display=f"Kiállította: {(fine.issuer.name if fine.issuer else "Rendszer")}")
            type_node: ActionNode = ActionNode("type_node", display=f"Típus: {fine.fine_type.name}")
            date_node: ActionNode = ActionNode("date_node", display=f"Dátum: {fine.issued:%Y.%m.%d}")
            amount_node: ActionNode = ActionNode("amount_node", display=f"Összeg: {format_numbers(fine.amount)} Ft")
            payed_amount_node: ActionNode = ActionNode("payed_amount_node",
                                                       display=f"Kifizetett összeg: {format_numbers(fine.payed_amount)} Ft")

            delete_node: ActionNode = ActionNode("info_action", display=f"Törlés")
            delete_node.response_handler = delete_fine_handler
            delete_node.response_handler_parameters = fine.id, target_player.id,
            delete_node.back_to_root = True

            fine_node.add_child(issuer_node)
            fine_node.add_child(type_node)
            fine_node.add_child(date_node)
            fine_node.add_child(amount_node)
            fine_node.add_child(payed_amount_node)
            fine_node.add_child(delete_node)

        dialog_tree.add_root(fine_list_node)

        dialog_tree.show_root_dialog(player)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def setweather(player: Player, weather_id: int):
    for i in Player.get_registry_items():
        i.set_weather(int(weather_id))


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def settime(player: Player, time: int):
    for i in Player.get_registry_items():
        i.set_time(int(time), 0)

    set_world_time(int(time))


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def saveint(player: Player, *args):
    InteriorDB.create(player.x, player.y, player.z, player.a, player.interior, *args)


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def gotoint(player: Player, interior_id: int) -> None:
    id = int(interior_id)

    if id == 0: player.set_interior(2); player.set_pos(1523.5098, -47.8211, 1002.2699)
    if id == 1: player.set_interior(11); player.set_pos(2003.1178, 1015.1948, 36.008)
    if id == 2: player.set_interior(5); player.set_pos(770.8033, -0.7033, 1000.7267)
    if id == 3: player.set_interior(3); player.set_pos(974.0177, -9.5937, 1001.1484)
    if id == 4: player.set_interior(3); player.set_pos(961.9308, -51.9071, 1001.1172)
    if id == 5: player.set_interior(3); player.set_pos(830.6016, 5.9404, 1004.1797)
    if id == 6: player.set_interior(3); player.set_pos(1037.8276, 0.397, 1001.2845)
    if id == 7: player.set_interior(3); player.set_pos(1212.1489, -28.5388, 1000.9531)
    if id == 8: player.set_interior(18); player.set_pos(1290.4106, 1.9512, 1001.0201)
    if id == 9: player.set_interior(1); player.set_pos(1412.1472, -2.2836, 1000.9241)
    if id == 10: player.set_interior(3); player.set_pos(1527.0468, -12.0236, 1002.0971)

    if id == 11: player.set_interior(3); player.set_pos(612.2191, -123.9028, 997.9922)
    if id == 12: player.set_interior(3); player.set_pos(512.9291, -11.6929, 1001.5653)
    if id == 13: player.set_interior(3); player.set_pos(418.4666, -80.4595, 1001.8047)
    if id == 14: player.set_interior(3); player.set_pos(386.5259, 173.6381, 1008.3828)
    if id == 15: player.set_interior(3); player.set_pos(288.4723, 170.0647, 1007.1794)
    if id == 16: player.set_interior(3); player.set_pos(206.4627, -137.7076, 1003.0938)
    if id == 17: player.set_interior(3); player.set_pos(-100.2674, -22.9376, 1000.7188)
    if id == 18: player.set_interior(3); player.set_pos(-201.2236, -43.2465, 1002.2734)
    if id == 19: player.set_interior(17); player.set_pos(-202.9381, -6.7006, 1002.2734)
    if id == 20: player.set_interior(17); player.set_pos(-25.7220, -187.8216, 1003.5469)

    if id == 21: player.set_interior(5); player.set_pos(454.9853, -107.2548, 999.4376)
    if id == 22: player.set_interior(5); player.set_pos(372.5565, -131.3607, 1001.4922)
    if id == 23: player.set_interior(17); player.set_pos(378.026, -190.5155, 1000.6328)
    if id == 24: player.set_interior(7); player.set_pos(315.244, -140.8858, 999.6016)
    if id == 25: player.set_interior(5); player.set_pos(225.0306, -9.1838, 1002.218)
    if id == 26: player.set_interior(2); player.set_pos(611.3536, -77.5574, 997.9995)
    if id == 27: player.set_interior(10); player.set_pos(246.0688, 108.9703, 1003.2188)
    if id == 28: player.set_interior(10); player.set_pos(6.0856, -28.8966, 1003.5494)
    if id == 29: player.set_interior(7); player.set_pos(773.7318, -74.6957, 1000.6542)
    if id == 30: player.set_interior(1); player.set_pos(621.4528, -23.7289, 1000.9219)

    if id == 31: player.set_interior(1); player.set_pos(445.6003, -6.9823, 1000.7344)
    if id == 32: player.set_interior(1); player.set_pos(285.8361, -39.0166, 1001.5156)
    if id == 33: player.set_interior(1); player.set_pos(204.1174, -46.8047, 1001.8047)
    if id == 34: player.set_interior(1); player.set_pos(245.2307, 304.7632, 999.1484)
    if id == 35: player.set_interior(3); player.set_pos(290.623, 309.0622, 999.1484)
    if id == 36: player.set_interior(5); player.set_pos(322.5014, 303.6906, 999.1484)
    if id == 37: player.set_interior(1); player.set_pos(-2041.2334, 178.3969, 28.8465)
    if id == 38: player.set_interior(1); player.set_pos(-1402.6613, 106.3897, 1032.2734)
    if id == 39: player.set_interior(7); player.set_pos(-1403.0116, -250.4526, 1043.5341)
    if id == 40: player.set_interior(2); player.set_pos(1204.6689, -13.5429, 1000.9219)

    if id == 41: player.set_interior(10); player.set_pos(2016.1156, 1017.1541, 996.875)
    if id == 42: player.set_interior(1); player.set_pos(-741.8495, 493.0036, 1371.9766)
    if id == 43: player.set_interior(2); player.set_pos(2447.8704, -1704.4509, 1013.5078)
    if id == 44: player.set_interior(1); player.set_pos(2527.0176, -1679.2076, 1015.4986)
    if id == 45: player.set_interior(10); player.set_pos(-1129.8909, 1057.5424, 1346.4141)
    if id == 46: player.set_interior(3); player.set_pos(2496.0549, -1695.1749, 1014.7422)
    if id == 47: player.set_interior(10); player.set_pos(366.0248, -73.3478, 1001.5078)
    if id == 48: player.set_interior(1); player.set_pos(2233.9363, 1711.8038, 1011.6312)
    if id == 49: player.set_interior(2); player.set_pos(269.6405, 305.9512, 999.1484)
    if id == 50: player.set_interior(2); player.set_pos(414.2987, -18.8044, 1001.8047)

    if id == 51: player.set_interior(2); player.set_pos(1.1853, -3.2387, 999.4284)
    if id == 52: player.set_interior(18); player.set_pos(-30.9875, -89.6806, 1003.5469)
    if id == 53: player.set_interior(18); player.set_pos(161.4048, -94.2416, 1001.8047)
    if id == 54: player.set_interior(3); player.set_pos(-2638.8232, 1407.3395, 906.4609)
    if id == 55: player.set_interior(5); player.set_pos(1267.8407, -776.9587, 1091.9063)
    if id == 56: player.set_interior(2); player.set_pos(2536.5322, -1294.8425, 1044.125)
    if id == 57: player.set_interior(5); player.set_pos(2350.1597, -1181.0658, 1027.9766)
    if id == 58: player.set_interior(1); player.set_pos(-2158.6731, 642.09, 1052.375)
    if id == 59: player.set_interior(10); player.set_pos(419.8936, 2537.1155, 10)
    if id == 60: player.set_interior(14); player.set_pos(256.9047, -41.6537, 1002.0234)

    if id == 61: player.set_interior(14); player.set_pos(204.1658, -165.7678, 1000.5234)
    if id == 62: player.set_interior(12); player.set_pos(1133.35, -7.8462, 1000.6797)
    if id == 63: player.set_interior(14); player.set_pos(-1420.4277, 1616.9221, 1052.5313)
    if id == 64: player.set_interior(17); player.set_pos(493.1443, -24.2607, 1000.6797)
    if id == 65: player.set_interior(18); player.set_pos(1727.2853, -1642.9451, 20.2254)
    if id == 66: player.set_interior(16); player.set_pos(-202.842, -24.0325, 1002.2734)
    if id == 67: player.set_interior(5); player.set_pos(2233.6919, -1112.8107, 1050.8828)
    if id == 68: player.set_interior(6); player.set_pos(2194.7900, -1204.3500, 1049.0234)
    if id == 69: player.set_interior(9); player.set_pos(2319.1272, -1023.9562, 1050.2109)
    if id == 70: player.set_interior(10); player.set_pos(2261.0977, -1137.8833, 1050.6328)

    if id == 71: player.set_interior(17); player.set_pos(-944.2402, 1886.1536, 5.0051)
    if id == 72: player.set_interior(16); player.set_pos(-26.1856, -140.9164, 1003.5469)
    if id == 73: player.set_interior(15); player.set_pos(2217.281, -1150.5349, 1025.7969)
    if id == 74: player.set_interior(1); player.set_pos(1.5491, 23.3183, 1199.5938)
    if id == 75: player.set_interior(1); player.set_pos(681.6216, -451.8933, -25.6172)
    if id == 76: player.set_interior(3); player.set_pos(234.6087, 1187.8195, 1080.2578)
    if id == 77: player.set_interior(2); player.set_pos(225.5707, 1240.0643, 1082.1406)
    if id == 78: player.set_interior(1); player.set_pos(224.288, 1289.1907, 1082.1406)
    if id == 79: player.set_interior(5); player.set_pos(239.2819, 1114.1991, 1080.9922)
    if id == 80: player.set_interior(15); player.set_pos(207.5219, -109.7448, 1005.1328)

    if id == 81: player.set_interior(15); player.set_pos(295.1391, 1473.3719, 1080.2578)
    if id == 82: player.set_interior(15); player.set_pos(-1417.8927, 932.4482, 1041.5313)
    if id == 83: player.set_interior(12); player.set_pos(446.3247, 509.9662, 1001.4195)
    if id == 84: player.set_interior(0); player.set_pos(2306.3826, -15.2365, 26.7496)
    if id == 85: player.set_interior(0); player.set_pos(2331.8984, 6.7816, 26.5032)
    if id == 86: player.set_interior(0); player.set_pos(663.0588, -573.6274, 16.3359)
    if id == 87: player.set_interior(18); player.set_pos(-227.5703, 1401.5544, 27.7656)
    if id == 88: player.set_interior(0); player.set_pos(-688.1496, 942.0826, 13.6328)
    if id == 89: player.set_interior(0); player.set_pos(-1916.1268, 714.8617, 46.5625)
    if id == 90: player.set_interior(0); player.set_pos(818.7714, -1102.8689, 25.794)

    if id == 91: player.set_interior(0); player.set_pos(255.2083, -59.6753, 1.5703)
    if id == 92: player.set_interior(2); player.set_pos(446.626, 1397.738, 1084.3047)
    if id == 93: player.set_interior(5); player.set_pos(318.5645, 1118.2079, 1083.8828)
    if id == 94: player.set_interior(5); player.set_pos(227.7559, 1114.3844, 1080.9922)
    if id == 95: player.set_interior(4); player.set_pos(261.1165, 1287.2197, 1080.2578)
    if id == 96: player.set_interior(4); player.set_pos(286.1490, -84.5633, 1001.5156)
    if id == 97: player.set_interior(4); player.set_pos(449.0172, -88.9894, 999.5547)
    if id == 98: player.set_interior(4); player.set_pos(-27.844, -26.6737, 1003.5573)
    if id == 99: player.set_interior(0); player.set_pos(2135.2004, -2276.2815, 20.6719)
    if id == 100: player.set_interior(4); player.set_pos(306.1966, 307.819, 1003.3047)

    if id == 101: player.set_interior(10); player.set_pos(24.3769, 1341.1829, 1084.375)
    if id == 102: player.set_interior(1); player.set_pos(963.0586, 2159.7563, 1011.0303)
    if id == 103: player.set_interior(0); player.set_pos(2548.4807, 2823.7429, 10.8203)
    if id == 104: player.set_interior(0); player.set_pos(215.1515, 1874.0579, 13.1406)
    if id == 105: player.set_interior(4); player.set_pos(221.6766, 1142.4962, 1082.6094)
    if id == 106: player.set_interior(12); player.set_pos(2323.7063, -1147.6509, 1050.7101)
    if id == 107: player.set_interior(6); player.set_pos(344.9984, 307.1824, 999.1557)
    if id == 108: player.set_interior(12); player.set_pos(411.9707, -51.9217, 1001.8984)
    if id == 109: player.set_interior(4); player.set_pos(-1421.5618, -663.8262, 1059.5569)
    if id == 110: player.set_interior(6); player.set_pos(773.8887, -47.7698, 1000.5859)

    if id == 111: player.set_interior(6); player.set_pos(246.6695, 65.8039, 1003.6406)
    if id == 112: player.set_interior(14); player.set_pos(-1864.9434, 55.7325, 1055.5276)
    if id == 113: player.set_interior(4); player.set_pos(-262.1759, 1456.6158, 1084.3672)
    if id == 114: player.set_interior(5); player.set_pos(22.861, 1404.9165, 1084.4297)
    if id == 115: player.set_interior(5); player.set_pos(140.3679, 1367.8837, 1083.8621)
    if id == 116: player.set_interior(3); player.set_pos(1494.8589, 1306.48, 1093.2953)
    if id == 117: player.set_interior(14); player.set_pos(-1813.213, -58.012, 1058.9641)
    if id == 118: player.set_interior(16); player.set_pos(-1401.067, 1265.3706, 1039.8672)
    if id == 119: player.set_interior(6); player.set_pos(234.2826, 1065.229, 1084.2101)
    if id == 120: player.set_interior(6); player.set_pos(-68.5145, 1353.8485, 1080.2109)

    if id == 121: player.set_interior(6); player.set_pos(-2240.1028, 136.973, 1035.4141)
    if id == 122: player.set_interior(6); player.set_pos(297.144, -109.8702, 1001.5156)
    if id == 123: player.set_interior(6); player.set_pos(316.5025, -167.6272, 999.5938)
    if id == 124: player.set_interior(15); player.set_pos(-285.2511, 1471.197, 1084.375)
    if id == 125: player.set_interior(6); player.set_pos(-26.8339, -55.5846, 1003.5469)
    if id == 126: player.set_interior(6); player.set_pos(442.1295, -52.4782, 999.7167)
    if id == 127: player.set_interior(2); player.set_pos(2182.2017, 1628.5848, 1043.8723)
    if id == 128: player.set_interior(6); player.set_pos(748.4623, 1438.2378, 1102.9531)
    if id == 129: player.set_interior(8); player.set_pos(2807.3604, -1171.7048, 1025.5703)
    if id == 130: player.set_interior(9); player.set_pos(366.0002, -9.4338, 1001.8516)

    if id == 131: player.set_interior(1); player.set_pos(2216.1282, -1076.3052, 1050.4844)
    if id == 132: player.set_interior(1); player.set_pos(2268.5156, 1647.7682, 1084.2344)
    if id == 133: player.set_interior(2); player.set_pos(2236.6997, -1078.9478, 1049.0234)
    if id == 134: player.set_interior(3); player.set_pos(-2031.1196, -115.8287, 1035.1719)
    if id == 135: player.set_interior(8); player.set_pos(2365.1089, -1133.0795, 1050.875)
    if id == 136: player.set_interior(0); player.set_pos(1168.512, 1360.1145, 10.9293)
    if id == 137: player.set_interior(9); player.set_pos(315.4544, 976.5972, 1960.8511)
    if id == 138: player.set_interior(10); player.set_pos(1893.0731, 1017.8958, 31.8828)
    if id == 139: player.set_interior(11); player.set_pos(501.9578, -70.5648, 998.7578)
    if id == 140: player.set_interior(8); player.set_pos(-42.5267, 1408.23, 1084.4297)

    if id == 141: player.set_interior(11); player.set_pos(2282.9099, -1138.2900, 1050.8984)
    if id == 142: player.set_interior(9); player.set_pos(84.9244, 1324.2983, 1083.8594)
    if id == 143: player.set_interior(9); player.set_pos(260.7421, 1238.2261, 1084.2578)
    if id == 144: player.set_interior(0); player.set_pos(-1658.1656, 1215.0002, 7.25)
    if id == 145: player.set_interior(0); player.set_pos(-1961.6281, 295.2378, 35.4688)
