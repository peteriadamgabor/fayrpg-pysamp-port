import datetime
import random

from pysamp import set_timer
from python.fractions.shared.functions import send_call_to_fraction

from python.model.database import Player as PlayerDB

from python.model.dto import Player as PlayerDTO

from python.model.server import House, Player
from python.model.transorm import Transform
from python.utils.enums.colors import Color
from python.utils.enums.fractrion_types import FractionTypes
from python.utils.globals import HOUSE_VIRTUAL_WORD
from python.utils.helper.python import format_numbers


@Player.using_registry
def print_house_info(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    player.send_system_message(-1, f"|________Fay utca {house.id}________|")

    if house.owner is not None:
        player.send_system_message(-1, f"Tulajdonos: {house.owner.name}")
        
    else:
        if house.type == 0:
            player.send_system_message(-1, f"Ár: {format_numbers(house.price + house.house_type.price)} Ft | Leírás: {house.house_type.description}")
        else:
            player.send_system_message(-1, f"Ár: {format_numbers(house.price)} Ft / nap | Leírás: {house.house_type.description}")


@Player.using_registry
def buy_house(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    if not player.transfer_money(house.price + house.house_type.price):
        return

    player.send_system_message(Color.GREEN, f"Sikeresen megvetted a(z) {{AA3333}}{house.id}{{33AA33}} számú házat!")
    house.refresh_pickup(1239)
    house.owner = Transform.get_dto(PlayerDB, PlayerDTO, player.dbid)


@Player.using_registry
def rent_house(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    if not input_text.isdigit():
        player.send_system_message(Color.RED, "Számmal kell megadni!")
        return

    if not player.transfer_money((house.price) * int(input_text)):
        return

    house.rent_date = datetime.datetime.now() + datetime.timedelta(days=int(input_text))
    house.refresh_pickup(1239)
    house.owner = player.dbid

    player.send_system_message(Color.GREEN, f"Sikeresen kibérelted a(z) {{AA3333}}{house.id}{{33AA33}} számú házat!")
    player.send_system_message(Color.GREEN, f"{{AA3333}}{input_text}{{33AA33}} napra! Bérlés lejárata: {house.rent_date:%Y.%m.%d}")


@Player.using_registry
def lock_house(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    if house.locked:
        player.send_system_message(Color.GREEN, "Sikeresen kinyitottad a házad")
        house.locked = False
    else:
        player.send_system_message(Color.GREEN, "Sikeresen bezártad a házad")
        house.locked = True


@Player.using_registry
def sell_house(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    house.owner = None
    house.is_spawn = False

    player.send_system_message(Color.GREEN, "(( Sikeresen eladtad a házad! ))")
    player.money += int((house.price + house.house_type.price) * .75)
    house.refresh_pickup(1273)

@Player.using_registry
def cancel_rent(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    house.owner = None
    player.send_system_message(Color.GREEN, "Sikeresen lemondtad a bérlést!")
    house.refresh_pickup(1272)


@Player.using_registry
def extend_rent(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    if not input_text.isdigit():
        player.send_system_message(Color.RED, "Számmal kell megadni!")

    days = int(input_text)

    if not player.transfer_money(house.price * days):
        return

    house.rent_date += datetime.timedelta(days=days)
    player.send_system_message(Color.GREEN, f"Sikeresen meghosszabítottad a(z) {{AA3333}}{house.id}{{33AA33}} számú ház bárlését! {{AA3333}}{input_text}{{33AA33}} nappal!\nBérlés lejárata: {{AA3333}}{house.rent_date:%Y.%m.%d}{{33AA33}}")


@Player.using_registry
def enter_house(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    if house.locked:
        player.send_system_message(Color.RED, "A ház zárva van!")
        return

    player.set_pos(house.house_type.enter_x, house.house_type.enter_y, house.house_type.enter_z)
    player.set_interior(house.house_type.interior)
    player.set_facing_angle(house.house_type.angle)
    player.set_virtual_world(HOUSE_VIRTUAL_WORD + house.id)


@Player.using_registry
def set_spawn_house(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    house: House = args[0]

    if not house.is_spawn:
        spwn_house = player.get_spawn_hous()
        
        if spwn_house:
            player.clear_spawn_house()
            player.send_system_message(Color.GREEN, f"Sikeresen átjelentkeztél a(z) {{AA3333}}{house.id}{{33AA33}} számú házba!\nA(z) {{AA3333}}{spwn_house.id}{{33AA33}} számú házból kilettél jelentve!")
        else:
            player.send_system_message(Color.GREEN, f"Sikeresen bejelentkeztél a(z) {{AA3333}}{house.id}{{33AA33}} számú házba!")

        house.is_spawn = True
    
    else:
        player.send_system_message(Color.GREEN, f"Sikeresen kijelentkeztél a(z) {{AA3333}}{house.id}{{33AA33}} számú házból!")
        house.is_spawn = False


@Player.using_registry
def crack_lock_house(player: Player, response: int, list_item: int, input_text: str, house: House, *args, **kwargs):
    if not player.have_item("Csavarhúzó") and not player.have_item("Kalapács"):
        player.send_system_message_multi_lang(Color.ORANGE, "Nincs nálad eszköz amivel fel tudnát törni a zárat!")
        return

    if house.lockpick_time >= 3:
        player.send_system_message_multi_lang(Color.ORANGE, "Ezt a zárat nem tudod feltörni!")
        return

    player.start_action("BOMBER","BOM_Plant_Loop", True,
                        "~b~Zár feltörése...", random.randint(8, 22), "elkezd babrálni a zárral",
                        crack_lock, house)

    set_timer(neighbor_notify_police, random.randint(5, 17) * 1000, False, player, house)


def crack_lock(player: Player, house: House):
    base_success = .66
    base_alarm_trigger = 0.25
    success = 0.0
    triggerd = 0.0

    lock_rng: float = random.random()
    alarm_rng: float = random.random()

    house.lockpick_time += 1

    if player.have_item("Csavarhúzó"):
        success = base_success - (0.19 + (0.05 * (house.door_lvl + 1)))
        if house.alarm_lvl > 0:
            triggerd = (base_alarm_trigger + (0.07 * house.alarm_lvl + 1) - 0.15)

    elif player.have_item("Kalapács"):
        success = base_success - (0.05 * (house.door_lvl + 1))
        if house.alarm_lvl > 0:
            triggerd = (base_alarm_trigger + (0.07 * house.alarm_lvl + 1))

    if lock_rng < success:
        player.send_system_message_multi_lang(Color.GREEN, "Sikertült feltörnöd a zárat! Most már be tudsz menni!")
        player.make_action("feltörte a zárat")
        house.locked = False
        house.is_robbed = False

    else:
        player.send_system_message_multi_lang(Color.GREEN, "Nem sikerült feltörni a zárat!")
        player.make_action("nem tudta feltört a zárat")

    if alarm_rng < triggerd:
        house.is_alarmed = True
    return


def neighbor_notify_police(player: Player, house: House) -> None:
    player_count: int = player.count_near_by_players(15.0)
    random_value: float = random.random()
    notice_random_value: float = random.random()
    probability: int = 25
    notice: int = 6

    if player_count <= 2:
        probability += 5.0 + (house.lockpick_time / 100.0 )
        notice += 1.0
    elif player_count <= 4:
        probability += 15.0 + (house.lockpick_time / 100.0 )
        notice += 12.0
    else:
        probability = 100.0
        notice += 45.0

    if random_value < probability / 100.0:
        msg_int: int = random.randint(0, 4)

        if msg_int == 0:
            msg = f"** BEJELENTÉS: Gyanús mozgást jeleztek a szomszédok a(z) {house.id} háznál.\nEgységet kérünk az eset kivizsgálásához!"
        elif msg_int == 1:
            msg = f"** BEJELENTÉS: Ismeretlen személyeket láttak a(z) {house.id} ház körül.\nEgységet kérünk az eset kivizsgálásához!"
        elif msg_int == 2:
            msg = f"** BEJELENTÉS: Gyanús tevékenységet észleltek a(z) {house.id} címen .\nEgységet kérünk az eset kivizsgálásához!"
        elif msg_int == 3:
            msg = f"** BEJELENTÉS: A(z) {house.id} címnél a szomszédok szerint idegenek járkálnak a kertben.\nEgységet kérünk az eset kivizsgálásához!"
        else:
            msg = f"** BEJELENTÉS: A(z) {house.id} címnél a vérlehtőleg betörés folyik.\nEgységet kérünk az eset kivizsgálásához!"

        send_call_to_fraction(FractionTypes.LAW_ENFORCEMENT, msg, (house.entry_x, house.entry_y, house.entry_z), None)

        if notice_random_value < notice / 100.0:
            player.send_system_message_multi_lang(Color.ORANGE, "A szomszédok megláthattak! Vigyázzz, lehet, hogy értesítették a rendőröket!")
