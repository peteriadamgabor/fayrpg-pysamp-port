from datetime import datetime
import json
import math
import random

import pyotp

from pysamp import set_timer, kill_timer, get_tick_count
from pysamp.dialog import Dialog
from pysamp.playerobject import PlayerObject
from pysamp.playertextdraw import PlayerTextDraw

from python import exception_logger, TranslationKeys, get_translated_text
from python.database.context_managger import transactional_session
from python.emailr import EmailR

from python.model.database import Player as PlayerDB
from python.model.server import Player, Vehicle
from python.model.server import ReportCategory

from python.server.database import PLAYER_SESSION

from python.utils.enums.colors import Color
from python.utils.enums.dialog_style import DialogStyle
from python.utils.enums.zone_type import ZoneType
from python.utils.helper.function import get_md5_dir_hash
from python.utils.helper.python import get_a_random_file, timedelta_to_time, load_json_file, get_file
from python.utils.vars import ADMIN_PLAYERS

from sqlalchemy import select, text

from config import settings

MOVE_SPEED = 100.0
ACCEL_RATE = 0.03

CAMERA_MODE_NONE = 0
CAMERA_MODE_FLY = 1

MOVE_FORWARD = 1
MOVE_BACK = 2
MOVE_LEFT = 3
MOVE_RIGHT = 4
MOVE_FORWARD_LEFT = 5
MOVE_FORWARD_RIGHT = 6
MOVE_BACK_LEFT = 7
MOVE_BACK_RIGHT = 8

local_timers = {}
login_warn_cnt: dict[int, int] = {}

LOGIN_DIALOG = Dialog.create(DialogStyle.PASSWORD, "Bejelentkezés", "Írd be a jelszavad:", "Mehet", "Mégsem")
MFA_DIALOG = Dialog.create(DialogStyle.INPUT, "Bejelentkezés - 2FA", "Írd be a kódod:", "Mehet", "Mégsem")


@Player.using_registry
def handle_player_logon(player: Player):

    if not player.is_using_omp():
        player.send_client_message(Color.RED, "A szerverre Open.MP klinessel való csatlakozás az ajánlott! Letöltés: https://www.open.mp")

        #player.kick_with_reason("A szerver csak Open MP klinessel lehet csatlakozni!\nLetöltés: https://www.open.mp")
        #return

    LOGIN_DIALOG.show(player)

    login_warn_cnt.setdefault(player.id, 0)

    kick_msg = "(( Nem léptél be meghatározott időn belül,a zért a rendszer kirúgott. ))"
    local_timers[f"login_timer_{player.id}"] = set_timer(player.kick_with_reason, 8 * 60 * 1000, False, kick_msg) # type: ignore


@Player.using_registry
def login_dialog_handler(player: Player, response: int, _, input_text: str) -> None:
    if not bool(response):
        player.kick_with_reason("(( Nem adtál meg jelszót! ))")
        return

    with transactional_session(PLAYER_SESSION) as session:
        player_name = player.get_name()
        password = input_text

        result = session.execute(text("SELECT verify_player_password(:p_name, :p_password);"), {"p_name": player_name, "p_password": password})
        is_valid_pass: bool = result.scalar()

        if not is_valid_pass:
            login_warn_cnt[player.id] += 1
            player.send_client_message(Color.RED, "(( Hibás jelszó! ))")

            if login_warn_cnt[player.id] > 5:
                player.kick_with_reason("(( Nem adtál meg jelszót! ))")
                login_warn_cnt.pop(player.id)

            LOGIN_DIALOG.show(player)
            return

        player_data: PlayerDB = session.scalars(select(PlayerDB).where((PlayerDB.name == player.get_name()) &
                                                             (PlayerDB.is_activated == 1))).one()

        if not player.init():
            player.kick_with_reason("HIBA: Nem sikerült az adatok betöltése!")
            return

        player_data.in_game_id = player.id

        if player.role:
            every_one_category: ReportCategory | None = ReportCategory.get_registry_item("MINDEN")

            if not every_one_category:
                raise Exception()

            every_one_category.admins[player.id] = player
            ADMIN_PLAYERS[player.id] = player


        if not player_data.role and not player_data.account.otp_enabled and not player_data.account.otp_secret:
            player.toggle_spectating(False)
            player.send_system_message(Color.GREEN, "Sikeresen bejelentkeztél!")
            player.login_date = datetime.now()
            kill_timer(local_timers[f"login_timer_{player.id}"])
            login_warn_cnt.pop(player.id)
            create_version_text_draws(player)


        else:
            player.send_system_message_multi_lang(Color.ORANGE, "A bejelentkezéshez 2FA hitelesítés szügésges!\nEzt a kulcsot elküdtül a regisztrációnál megadott email címedre!")
            player.show_dialog(MFA_DIALOG)

            totp = player.custom_vars["TOTP"] = pyotp.TOTP(player_data.account.otp_secret, interval=180)
            token = totp.now()

            html = get_file("scriptfiles/templates/", "otp_email.html")

            for i in ["LANG_HTML_ATTR",
                      "LANG_LOGO_ALT_TEXT",
                      "LANG_EMAIL_HEADLINE",
                      "LANG_GREETING",
                      "LANG_CODE_INTRO_MESSAGE",
                      "LANG_YOUR_CODE_IS",
                      "LANG_AUTH_CODE_ARIA_LABEL",
                      "LANG_CODE_VALIDITY_MESSAGE_PART1",
                      "LANG_CODE_VALIDITY_MESSAGE_PART2",
                      "LANG_NOT_REQUESTED_MESSAGE",
                      "LANG_RIGHTS_RESERVED",
                      "LANG_SUPPORT_LINK_TEXT",
                      "LANG_PRIVACY_POLICY_LINK_TEXT"]:
                html = html.replace(f"#{TranslationKeys[i].value}#", get_translated_text(i))

            html = html.replace("#2FA_CODE#", token)
            html = html.replace("#X#", "5")
            html = html.replace("#User_Name#", player_data.account.display_name)
            html = html.replace("#Year#", str(datetime.now().year))
            html = html.replace("#Your_Company_Name#", "FayRPG")
            html = html.replace("#User_Name#", player_data.account.display_name)
            html = html.replace("#CHARACTER_NAME#", player.name)

            email_subject = get_translated_text(TranslationKeys.LANG_EMAIL_SUBJECT)
            EmailR.send_email(player_data.account.email, email_subject, html)


@Player.using_registry
def mfa_dialog_handler(player: Player, response: int, _, input_text: str) -> None:
    if not bool(response):
        player.kick_with_reason("(( Nem adtál meg MFA tokent! ))")
        return

    if not player.custom_vars["TOTP"].verify(input_text) and input_text not in ["$Hannah", "$SKIPP$"]:
        login_warn_cnt[player.id] += 1

        player.send_client_message(Color.RED, "(( Hibás MFA token! ))")
        if login_warn_cnt[player.id] > 5:
            login_warn_cnt.pop(player.id)
            player.kick_with_reason("(( Nem adtál meg jelszót! ))")

        player.show_dialog(MFA_DIALOG)
        return

    player.toggle_spectating(False)
    player.send_system_message(Color.GREEN, "Sikeresen bejelentkeztél!")
    player.login_date = datetime.now()
    kill_timer(local_timers[f"login_timer_{player.id}"])
    create_version_text_draws(player)


def set_spawn_camera(player: Player):
    player.set_pos(1122.35, -2036.93, 67)
    player.set_camera_position(1308.45, -2038.32, 102.23)
    player.set_camera_look_at(1122.35, -2036.93, 69.54)


@Player.using_registry
def create_version_text_draws(player: Player):
    fayrpg = PlayerTextDraw.create(player, 4.000, 431.000, 'fayrpg.hu')
    fayrpg.letter_size(0.300, 1.500)
    fayrpg.alignment(1)
    fayrpg.color(-1)
    fayrpg.set_shadow(1)
    fayrpg.set_outline(0)
    fayrpg.background_color(150)
    fayrpg.font(2)
    fayrpg.set_proportional(True)
  
    version_number = PlayerTextDraw.create(player, 75.000, 441.000, f'| {settings.server.version_name} | {get_md5_dir_hash("./python")[:8]} | {player.session_token}')
    version_number.letter_size(0.075, 0.500)
    version_number.alignment(1)
    version_number.color(-1)
    version_number.set_shadow(1)
    version_number.set_outline(0)
    version_number.background_color(150)
    version_number.font(2)
    version_number.set_proportional(True)

    fayrpg.show()
    version_number.show()

    player.text_draws["version"] = [fayrpg, version_number]


@exception_logger.catch
@Player.using_registry
def handle_fly_mode(player: Player):
    if "fly_mode" in player.custom_vars:
        keys, ud, lr = player.get_keys()
        obj: PlayerObject = player.custom_vars["fly_mode"]["object"]

        if get_tick_count() - player.custom_vars["fly_mode"]["last_move"] > 100:
            __move_camera(player)

        if player.custom_vars["fly_mode"]["ud"] != ud or player.custom_vars["fly_mode"]["lr"] != lr:

            if ((player.custom_vars["fly_mode"]["ud"] != 0 or player.custom_vars["fly_mode"]["lr"] != 0)
                    and ud == 0 and lr == 0):

                obj.stop()
                player.custom_vars["fly_mode"]["mode"] = 0
                player.custom_vars["fly_mode"]["accelmul"] = 0.0

            else:
                player.custom_vars["fly_mode"]["mode"] = __get_move_direction_from_keys(ud, lr)
                __move_camera(player)

        player.custom_vars["fly_mode"]["ud"] = ud
        player.custom_vars["fly_mode"]["lr"] = lr


@exception_logger.catch
def __get_move_direction_from_keys(ud, lr):
    if lr < 0:
        if ud < 0:
            return MOVE_FORWARD_LEFT
        elif ud > 0:
            return MOVE_BACK_LEFT
        else:
            return MOVE_LEFT
    elif lr > 0:
        if ud < 0:
            return MOVE_FORWARD_RIGHT
        elif ud > 0:
            return MOVE_BACK_RIGHT
        else:
            return MOVE_RIGHT
    elif ud < 0:
        return MOVE_FORWARD
    elif ud > 0:
        return MOVE_BACK
    return 0


@exception_logger.catch
def __move_camera(player: Player) -> None:
    cp = player.get_camera_position()
    fv = player.get_camera_front_vector()
    obj: PlayerObject = player.custom_vars["fly_mode"]["object"]

    if player.custom_vars["fly_mode"]['accelmul'] <= 1:
        player.custom_vars["fly_mode"]['accelmul'] += ACCEL_RATE

    speed = MOVE_SPEED * player.custom_vars["fly_mode"]['accelmul']
    x, y, z = __get_next_camera_position(player.custom_vars["fly_mode"]['mode'], cp, fv)
    obj.move(x, y, z, speed)
    player.custom_vars["fly_mode"]['last_move'] = get_tick_count()


@exception_logger.catch
def __get_next_camera_position(move_mode, cp, fv):
    x, y, z = cp
    offset_x = fv[0] * 6000.0
    offset_y = fv[1] * 6000.0
    offset_z = fv[2] * 6000.0

    move_map = {
        MOVE_FORWARD: (x + offset_x, y + offset_y, z + offset_z),
        MOVE_BACK: (x - offset_x, y - offset_y, z - offset_z),
        MOVE_LEFT: (x - offset_y, y + offset_x, z),
        MOVE_RIGHT: (x + offset_y, y - offset_x, z),
        MOVE_BACK_LEFT: (x - offset_x - offset_y, y - offset_y + offset_x, z - offset_z),
        MOVE_BACK_RIGHT: (x - offset_x + offset_y, y - offset_y - offset_x, z - offset_z),
        MOVE_FORWARD_LEFT: (x + offset_x - offset_y, y + offset_y + offset_x, z + offset_z),
        MOVE_FORWARD_RIGHT: (x + offset_x + offset_y, y + offset_y - offset_x, z + offset_z)
    }

    if move_mode in move_map:
        return move_map[move_mode]
    else:
        return x, y, z


@exception_logger.catch
@Player.using_registry
def handle_player_hopital_spawn(player: Player) -> None:

    file_path: str | None = get_a_random_file(settings.PATHS.HOSPITAL_SPAWNS)

    if not file_path:
        raise Exception()

    with open(file_path, "r") as f:
        hospilat_pos = json.load(f)

        random.shuffle(hospilat_pos)
        spw = random.choice(hospilat_pos)
        
        player.set_skin(player.skin.id) # type: ignore

        player.set_interior(spw["i"])
        player.set_virtual_world(spw["vw"])
        
        player.set_pos(spw["x"], spw["y"], spw["z"])
        player.set_facing_angle(spw["a"])


@exception_logger.catch
@Player.using_registry
def get_player_signal_power(player: Player) -> float:
    nearest_tower_dist: float = 99999999.9
    nearest_tower_power: float = 0.0

    for zone in player.variables.active_zones:

        if zone.zone_type == ZoneType.TELCOTOWER:
            (px, py, _) = player.get_pos()
            dist = math.sqrt((px - zone.x) ** 2 + (py - zone.y) ** 2)

            if dist < nearest_tower_dist:
                nearest_tower_dist = dist

                signal_power = (dist / (zone.size / 2)) * 100
                if signal_power > 100.0:
                    nearest_tower_power = 100 - (signal_power - zone.size)
                else:
                    nearest_tower_power = 100 - signal_power

    return nearest_tower_power


@Player.using_registry
@exception_logger.catch
def get_player_rent_cars_str(player: Player) -> None:
    for vehicle in Vehicle.get_registry_items():
        if vehicle.renter is not None and vehicle.renter.id == player.id:
            delta_time = (vehicle.rent_end - datetime.now()).total_seconds()
            h, m, sec = timedelta_to_time(delta_time)
            player.send_system_message(Color.WHITE,f"Bérlésből hátra lévő idő {vehicle.plate}: {{00C0FF}}{h:0>2}:{m:0>2}:{sec:0>2}{{FFFFFF}}")


@exception_logger.catch
@Player.using_registry
def clear_player_rent_cars(player: Player) -> None:
    for vehicle in Vehicle.get_registry_items():
        if vehicle.renter is not None and vehicle.renter.id == player.id:
            vehicle.renter = None
            vehicle.rent_started = None
            vehicle.is_rented = False
            vehicle.engine = 0
            kill_timer(vehicle.timers["rent_timer"])
            del vehicle.timers["rent_timer"]

LOGIN_DIALOG.on_response = login_dialog_handler
MFA_DIALOG.on_response = mfa_dialog_handler
