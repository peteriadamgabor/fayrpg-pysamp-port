from typing import Optional

from pyeSelect.eselect import MenuItem, Menu
from python.model.database import skin
from python.model.server import Player
from python.server.database import MAIN_SESSION
from python.utils.enums.colors import Color
from python.utils.enums.fractrion_types import FractionTypes
from python.utils.helper.function import get_weapon_max_ammo, get_weapon_slot_name, get_weapon_name
from python.model.dto import Fraction as FractionDTO

@Player.using_registry
def check_have_valid_fraction_skin(player: Player) -> bool:
    return player.fraction_skin.id in list_fraction_skin_ids(player.fraction.id, player.sex)


@Player.using_registry
def check_is_valid_fraction_skin(player: Player) -> bool:
    return player.get_skin() in list_fraction_skin_ids(player.fraction.id, player.sex)


@Player.using_registry
def change_fk_skin(player: Player, menu_item: MenuItem):
    player.send_client_message(Color.GREEN, "(( Sikeresen választottál ruhát! Allj szolgalatba! ))")
    player.fraction_skin = menu_item.model_id


@Player.using_registry
def select_new_fraction_skin(player: Player):
    menu = Menu(
        'Frakcio ruhak',
        [MenuItem(skin.id) for skin in list_fraction_skins(player.fraction.id, player.sex)],
        on_select=change_fk_skin,
    )

    menu.show(player)


def list_fraction_skins(fraction_id: int, sex: int) -> list[skin]:
    with MAIN_SESSION() as session:
        fraction: Fraction = session.query(Fraction).filter(Fraction.id == fraction_id).first()
        return [skin for skin in fraction.skins if skin.sex == bool(sex)]


def list_fraction_skin_ids(fraction_id: int, sex: int) -> list[int]:
    with MAIN_SESSION() as session:
        fraction: Fraction = session.query(Fraction).filter(Fraction.id == fraction_id).first()
        return [skin.id for skin in fraction.skins if skin.sex == bool(sex)]


def count_player_duty_weapons(player) -> int:
    count = 0

    for i in [1, 2, 9]:
        weapon, ammo = player.get_weapon_data(i)

        if weapon != 0 and ammo != 0:
            count += 1

    return count


@Player.using_registry
def make_locker_content(player: Player) -> str:
    locker_content = (f"Egyenruga:\t{'Szolgálati' if check_is_valid_fraction_skin(player) else 'Civil'}\n"
                      f"Szolgálat:\t{'{{AA3333}}Letétel' if player.in_duty else '{{33AA33}}Felvétel'}\n"
                      f"Felszerelés:\t{count_player_duty_weapons(player)}/3")

    return locker_content


@Player.using_registry
def make_locker_stuff(player: Player, weapon_slot_list=None) -> str:
    content_list = []
    if weapon_slot_list is None:
        weapon_slot_list = [1, 2, 9]

    for slot in weapon_slot_list:
        weapon_id, ammo = player.get_weapon_data(slot)

        magazine = 1 if slot in [1, 9] else 2
        max_ammo = get_weapon_max_ammo(weapon_id, magazine)
        weapon_name = "Nincs" if weapon_id == 0 else get_weapon_name(weapon_id)

        content_list.append(f"#slot~>{slot}#{get_weapon_slot_name(slot)}\t{weapon_name}\t{ammo}/{max_ammo}")
    return "\n".join(content_list)


@Player.using_registry
def make_locker_enable_weapons(player: Player, slot) -> str:
    content_list = []
    slot = int(slot)

    template = "#weapon_id~>{weapon_id}#{name}\tEgy tár kapacitás: {mag}"

    if slot == 1:
        for i in [3]:
            content_list.append(template.format(weapon_id=i, name=get_weapon_name(i), mag=get_weapon_max_ammo(i)))

    if slot == 2:
        for i in [23, 24]:
            content_list.append(template.format(weapon_id=i, name=get_weapon_name(i), mag=get_weapon_max_ammo(i, 2)))

    if slot == 9:
        for i in [41, 43]:
            content_list.append(template.format(weapon_id=i, name=get_weapon_name(i), mag=get_weapon_max_ammo(i, 1)))
    return "\n".join(content_list)


@Player.using_registry
def handel_locker_stuff_action(player: Player, response, list_item, input_text, *args) -> bool:
    if not player.in_duty:
        player.send_system_message(Color.GREEN, "Nem vagy szolgálatban így nem vehetsz magadhoz fegyvert!")
        return False

    given_weapon_id = int(args[0])
    slot = int(args[1])

    magazine = 1 if slot in [1, 9] else 2
    max_ammo = get_weapon_max_ammo(given_weapon_id, magazine)

    weapon_id, ammo = player.get_weapon_data(slot)

    if weapon_id == given_weapon_id and ammo > 0:
        player.set_armed_weapon(0)
        player.remove_weapon(given_weapon_id)
        player.send_system_message(Color.GREEN, "Visszaraked a fegyvert a szekrénybe!")

    elif weapon_id == given_weapon_id and ammo == 0:
        player.set_ammo(given_weapon_id, max_ammo)
        player.send_system_message(Color.GREEN, "A fegyvert sikeresen magadhoz vetted!")

    elif weapon_id != given_weapon_id and ammo >= 0:
        player.give_weapon(given_weapon_id, max_ammo)
        player.send_system_message(Color.GREEN, "A fegyvert sikeresen lecserélted!")

    elif weapon_id == 0 and ammo == 0:
        player.give_weapon(given_weapon_id, max_ammo)
        player.send_system_message(Color.GREEN, "A fegyvert sikeresen magadhoz vetted!")
    return True


@Player.using_registry
def change_duty_skin(player: Player, response: int, list_item: int, input_text: str, *args) -> bool:
    if player.in_duty and player.get_skin() in list_fraction_skin_ids(player.fraction.id, player.sex):
        player.send_system_message(Color.ORANGE, "Amíg szolgálatban vagy nem öltözhetsz át!")
        return False

    if player.get_skin() in list_fraction_skin_ids(player.fraction.id, player.sex):
        player.set_skin(player.skin.id)
        return True

    player.set_skin(player.fraction_skin.id)
    return True


@Player.using_registry
def handle_new_skin(player: Player, response: int, list_item: int, input_text: str, *args) -> bool:
    select_new_fraction_skin(player)
    return True


@Player.using_registry
def change_duty(player: Player, response: int, list_item: int, input_text: str, *args) -> bool:
    if not player.get_skin() in list_fraction_skin_ids(player.fraction.id, player.sex):
        player.send_system_message(Color.ORANGE, "Nem vagy szolgálati ruhában! Így nem veheted fel a szogálatot!")
        return False

    if player.in_duty:
        player.send_system_message(Color.GREEN, "Befejezted a szolgálatot!")
        player.send_system_message(Color.ORANGE, "Minden fegyvert vissza raktál a szekrénybe!")

    else:
        player.send_system_message(Color.GREEN, "Szolgalata álltal!")
        player.send_system_message(Color.ORANGE, "Minden fegyver ami a kezedbe volt el lett törölve!")

    player.fraction.duty_players.append(player) if player.in_duty else player.fraction.duty_players.remove(player)
    player.reset_weapons()
    player.in_duty = not player.in_duty
    return True


def send_call_to_fraction(fraction_type: int, msg: str, pos: tuple[float, float, float], caller: Optional[Player]) -> None:
    for fraction in FractionDTO.get_registry_items():
        if fraction.type == fraction_type:
            for player in fraction.duty_players:
                call_id: int = fraction.add_new_call(caller, pos)
                msg += (f"\nHívás kódszáma: {call_id}. {get_nearest_player_to_pos(fraction, pos).name} van a legközelebb.\n"
                        f"Ha el akarod fogadni a hívást: /elfogad {__get_accept_type_for_fraction(fraction_type)} [segélyhívás kódszáma]")
                player.send_system_message(Color.LIGHTBLUE, msg)


def get_nearest_player_to_pos(fraction: FractionDTO, pos: tuple[float, float, float]) -> Player:
    ret = None
    nearest_dist = 999999.9

    for player in fraction.duty_players:
        dist = player.distance_from_point(*pos)
        if dist < nearest_dist:
            ret = player
            nearest_dist = dist

    return ret


def send_fraction_system_msg(fraction_type: int, msg: str, *args) -> None:
    for fraction in FractionDTO.get_registry_items():
        if fraction.type == fraction_type:
            for player in fraction.duty_players:
                player.send_system_message_multi_lang(Color.LIGHTBLUE, msg, *args)


def __get_accept_type_for_fraction(fraction_type: int) -> str:
    match fraction_type:
        case FractionTypes.LAW_ENFORCEMENT:
            return "rendor"
        case FractionTypes.MEDICAL:
            return "mento"
        case FractionTypes.FIRE_DEPARTMENT:
            return "tuzolto"
        case _:
            return "HIBA"


def get_fraction_group_name(fraction_type: int) -> str:
    match fraction_type:
        case FractionTypes.LAW_ENFORCEMENT:
            return "RENDŐRSÉG"
        case FractionTypes.MEDICAL:
            return "MENTŐK"
        case FractionTypes.FIRE_DEPARTMENT:
            return "TŰZOLTÓK"
        case _:
            return "HIBA"
