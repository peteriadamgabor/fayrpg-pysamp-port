import random
from datetime import datetime

from sqlalchemy import select

from python.database.context_managger import transactional_session
from python.model.database import PlayerFine as PlayerFineDB
from python.model.server import House
from python.model.server import Player
from python.server.database import MAIN_SESSION
from python.utils.enums.colors import Color
from python.utils.enums.translation_keys import TranslationKeys
from python.utils.player import get_nearest_gate
from python.utils.helper.python import format_numbers, timedelta_to_time, try_parse_int
from python.utils.vars import FREQUENCIES, FREQUENCY_PLAYERS
from .functions import get_player_rent_cars_str, get_player_signal_power


@Player.command
@Player.using_registry
def penztarca(player: Player):
    player.send_system_message(Color.WHITE, f"A pénztárcádban jelenleg {{00C0FF}} {format_numbers(int(player.money))} {{FFFFFF}}Ft van.")


@Player.command
@Player.using_registry
def ido(player: Player):
    h, m, sec = timedelta_to_time(player.today_played + (datetime.now() - player.login_date).total_seconds())
    player.send_system_message(Color.WHITE, f"A pontos idő: {{00C0FF}}{datetime.now():%Y.%m.%d %X} {{FFFFFF}}")
    player.send_system_message(Color.WHITE, f"Ébren töltött idő: {{00C0FF}}{h:0>2}:{m:0>2}:{sec:0>2} {{FFFFFF}}")
    player.send_system_message(Color.WHITE, f"Legközelebbi esedékes étkezés időpontja: {{00C0FF}}{player.parameter.food_time:%Y.%m.%d %X} {{FFFFFF}}")

    if player.hospital_release_date and player.hospital_release_date > datetime.now():
        delta_time = (player.hospital_release_date - datetime.now()).total_seconds()
        player.hospital_time = delta_time
        h, m, sec = timedelta_to_time(delta_time)
        player.send_system_message(Color.WHITE,f"Kórházból hátralévő idő: {{00C0FF}}{h:0>2}:{m:0>2}:{sec:0>2}{{FFFFFF}}")
    else:
        player.hospital_time = 0

    get_player_rent_cars_str(player)
    player.make_action("megnézte az óráját")


@Player.command
@Player.using_registry
def adminok(player: Player):
    player.send_system_message(Color.WHITE, "Online adminok:")

    for lplayer in Player.get_registry_items():
        if lplayer.role is None:
            continue

        if lplayer.role:
            cat = lplayer.report_category

            if player.role:
                a_str = f"{{F81414}}{lplayer.name}{{FFFFFF}} | Szint:" f"{{F81414}} {lplayer.role.name} - {cat} {{FFFFFF}}"
                player.send_system_message(Color.WHITE, a_str)
            else:
                p_str = f"{{F81414}}{lplayer.name}{{FFFFFF}} | Szint:" f"{{F81414}} {lplayer.role.name} {"- AFK" if cat == "AFK" else ""} {{FFFFFF}}"
                player.send_system_message(Color.WHITE, p_str)


@Player.command
@Player.using_registry
def nyit(player: Player):
    (x, y, z) = player.get_pos()
    _ = player.get_interior()
    _ = player.get_virtual_world()

    gate = get_nearest_gate((x, y, z))

    if gate:
        gate.open()

        if gate.auto:
            player.send_system_message(Color.WHITE, f"A kapu / ajtó {gate.close_time} másodperc múlva záródik!")
        else:
            player.send_system_message(Color.WHITE, f"Ez a kapu / ajtó manuális, nem záródik autómatikusan!")

    else:
        player.send_system_message(Color.RED, "Nincs a közelben ajtó / kapu amit ki tudnál nyitni!")


@Player.command
@Player.using_registry
def zar(player: Player):
    (x, y, z) = player.get_pos()
    _ = player.get_interior()
    _ = player.get_virtual_world()

    gate = get_nearest_gate((x, y, z))

    if gate:
        gate.close()

    else:
        player.send_system_message(Color.RED, "Nincs a közelben ajtó / kapu amit be tudnál zárni!")


@Player.command
@Player.using_registry
def torol(player: Player):
    player.disable_checkpoint()


@Player.command
@Player.using_registry
def szemelyi(player: Player):
    rng = random.Random(player.dbid + 23)

    chars = "".join([chr(rng.randint(65, 90)) for _ in range(2)])
    nums = f"{rng.randint(0, 999999):0>6}"

    player.broadcast_system_message(Color.WHITE, "|__________SZ E M É LY A Z O N O S Í T Ó I G A Z O L V Á NY__________|", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Név: {{00C0FF}}{player.name}{{FFFFFF}}", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Születési idő: {{00C0FF}}{player.birthdate}{{FFFFFF}}", 5.0)
    player.broadcast_system_message(Color.WHITE, "Nem: {00C0FF}" + ("Nő" if player.sex else "Férfi") + "{FFFFFF}", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Okmányazonosító: {{00C0FF}} {nums + chars}{{FFFFFF}}", 5.0)
    player.make_action("megmutatja a szemelyigazolványát")

@Player.command
@Player.using_registry
def lakcimkartya(player: Player):
    rng = random.Random(player.dbid + 79)

    chars = "".join([chr(rng.randint(65, 90)) for _ in range(2)])
    nums = f"{rng.randint(0, 999999):0>6}"

    spawn_house: House | None = player.get_spawn_hous()

    player.broadcast_system_message(Color.WHITE, "|__________L A K C Í M I G A Z O L V Á NY__________|", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Név:{{00C0FF}} {player.name}{{FFFFFF}}", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Okmányazonosító:{{00C0FF}} {nums} {chars}{{FFFFFF}}", 5.0)
    player.broadcast_system_message(Color.WHITE, f"Személyi azonosító: {{00C0FF}} {int(player.sex) + 1 }-{player.birthdate:%y%m%d}-{player.dbid}{{FFFFFF}}", 5.0)

    if spawn_house:
        player.broadcast_system_message(Color.WHITE, f"Lakcím:{{00C0FF}} Los Santos Fay utca {spawn_house.id}{{FFFFFF}}", 5.0)
    else:
        player.broadcast_system_message(Color.WHITE, f"Lakcím:{{00C0FF}} Nincs bejelentett lakcíme{{FFFFFF}}", 5.0)

    player.make_action("megmutatja a lakcím kártyáját")


@Player.command
@Player.using_registry
def me(player: Player, *action: str):
    msg: str = " ".join(action)

    if len(msg) < 3:
        player.send_system_message(Color.ORANGE, "Túl rövid a jelentésed! Minimum 3 karakternek kell lennie!")
        return

    player.make_action(msg)


@Player.command(aliases=("try",))
@Player.using_registry
def probal(player: Player, *action: str):
    msg: str = " ".join(action)

    if len(msg) < 3:
        player.send_system_message(Color.ORANGE, "Túl rövid a jelentésed! Minimum 3 karakternek kell lennie!")
        return

    if random.randint(0, 10) in [random.randint(0, 10) for _ in range(5)] :
        msg = f"megpróbál(ja) {msg}, és sikerül neki!"
    else:
        msg = f"megpróbál(ja) {msg}, de nem sikerül neki!"

    player.broadcast_action_message(Color.TRY, msg, 30.0)


@Player.command(aliases=("fine",))
@Player.using_registry
def tartozas(player: Player, action: str = "NOT_SET", value: int = -1):
    if action not in ["kifizet", "pay", "info", "list"]:
        player.send_system_message_multi_lang(Color.WHITE, TranslationKeys.FINEPARAMS)
        return

    if action in ["kifizet", "pay"]:
        if (amount := try_parse_int(value)) is None or amount <= 0:
            player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
            return

        if player.money < amount:
            player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTENOUGHMONEY)
            return

        with transactional_session(MAIN_SESSION) as session:
            player_fines: list[PlayerFineDB] = list(session.scalars(select(PlayerFineDB).where((PlayerFineDB.player_id == player.dbid) & (PlayerFineDB.is_payed == False)).order_by(PlayerFineDB.issued)).all())

            rolling_amount = amount

            for fine in player_fines:
                if rolling_amount == 0:
                    break

                if rolling_amount >= (fine.amount - fine.payed_amount):
                    fine.payed_amount = (fine.amount - fine.payed_amount)
                    fine.is_payed = True
                    rolling_amount -= fine.amount 

                else:
                    fine.payed_amount += rolling_amount
                    rolling_amount = 0 

        player.send_system_message_multi_lang(Color.WHITE, TranslationKeys.FINEPAY, format_numbers(amount))

    if action in ["list", "info"]:
        with transactional_session(MAIN_SESSION) as session:
            player_fines: list[PlayerFineDB] = list(session.scalars(select(PlayerFineDB).where((PlayerFineDB.player_id == player.dbid) & (PlayerFineDB.is_payed == False))).all())

            for index, fine in enumerate(player_fines):
                player.send_system_message(Color.WHITE, f"# {index + 1} - {fine.issued:%Y.%m.%d} - {fine.fine_type.name} - {fine.reason} - {format_numbers((fine.amount - fine.payed_amount))} Ft")
            player.send_system_message_multi_lang(Color.WHITE, TranslationKeys.FINEINFO, format_numbers(sum((i.amount - i.payed_amount) for i in player_fines)))

@Player.command
@Player.using_registry
def csatorna(player: Player, s_frequency: int):
    if (frequency := try_parse_int(s_frequency)) is None or frequency <= 0:
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
        return

    if player.variables.frequency != -1: # type: ignore
        p_index = -1

        for index, _player in enumerate(FREQUENCY_PLAYERS[frequency]):
            if _player.id == player.id:
                p_index = index
                break

        FREQUENCY_PLAYERS[frequency].pop(p_index)

    if frequency in FREQUENCIES:
        freq = FREQUENCIES[frequency]

        if freq.fraction_id == player.fraction.id: # type: ignore
            FREQUENCY_PLAYERS[frequency].append(player)
            player.variables.frequency = frequency # type: ignore

            player.send_system_message(Color.GREEN, "Rádió frekvenzia sikeresen beállítva!")

            return

    player.send_system_message(Color.RADIO, "* [rádió]: folyamatos recsegés")


@Player.command
@Player.using_registry
def r(player: Player, msg: str):
    freq = player.variables.frequency # type: ignore
    signal = get_player_signal_power(player)

    if freq in FREQUENCY_PLAYERS and signal:
        for target_player in FREQUENCY_PLAYERS[freq]:
            target_player.send_system_message(Color.RADIO,
                                              f"* [rádió] {player.fraction.acronym} {player.rank.name} {player.name}: {msg}, vége **") # type: ignore

    else:
        player.send_system_message(Color.RADIO, "* [rádió]: folyamatos recsegés")
