from datetime import datetime

from sqlalchemy import select, text

from samp import CallRemoteFunction  # type: ignore

from pysamp import call_native_function, register_callback, set_game_mode_text, set_timer, set_world_time, send_rcon_command
from pystreamer import register_callbacks as pystreamer_register_callbacks
from pystreamer import set_visible_items as streamer_set_visible_items
from python.database.context_managger import transactional_session

from python.model.database import DutyLocation as DutyLocationDB
from python.model.database import Frequency as FrequencyDB
from python.model.database import Interior as InteriorDB
from python.model.database import TelCoTower as TelCoTowerDB
from python.model.database import Fraction as FractionDB
from python.model.database import Skin as SkinDB
from python.model.database import Player as PlayerDB
from python.model.database import FineType as FineTypeDB
from python.model.database import Role as RoleDB
from python.model.database import ReportCategory as ReportCategoryDB
from python.model.database import Command as CommandDB
from python.model.database import CommandPermission as CommandPermissionDB
from python.model.database import BusinessType as BusinessTypeDB
from python.model.database import Business as BusinessDB
from python.model.database import FuelType as FuelTypeDB
from python.model.database import House as HouseDB
from python.model.database import HouseType as HouseTypeDB
from python.model.database import VehicleModel as VehicleModelDB
from python.model.database import VehicleColor as VehicleColorDB
from python.model.database import Item as ItemDB
from python.model.database import Rank as RankDB

from python.model.dto import BusinessType as BusinessTypeDTO

from python.model.server import DutyPointDynamicZone
from python.model.server import DynamicZone
from python.model.server import Interior
from python.model.server import InteriortDynamicZone

from python.server.database import MAIN_SESSION

from python.utils.helper.function import get_md5_dir_hash
from python.utils.vars import FREQUENCY_PLAYERS, FREQUENCIES

from python.model.dto import DutyLocation
from python.model.dto import Fraction as FractionDTO
from python.model.transorm import Transform

from config import settings


SERVER_GLOBAL_TIMER: int = -1


def server_start():
    __load_default_db_records()

    global SERVER_GLOBAL_TIMER

    date_time = datetime.now()

    if date_time.minute == 0 and date_time.second == 0:
        SERVER_GLOBAL_TIMER = set_timer(__server_timer, 60 * 1000, True)
    else: 
        set_timer(__fractured_server_timer, (date_time.minute * 60 + date_time.second) * 1000, False)

    __clear_player_in_game_ids()

    send_rcon_command(f"name {settings.server.name}")
    send_rcon_command(f"password {settings.secrets.SERVER_PASSWORD}")

    if settings.server.is_developer:
        set_game_mode_text(f"{settings.server.mode} - DEV - [{get_md5_dir_hash("./python")[:8]}]")
    else:
        set_game_mode_text(f"{settings.server.mode} {settings.server.version_number}")
    
    load_teleports()
    load_duty_locations()
    load_interiors()
    load_telco_towers()
    load_frequencies()
    load_custom_skins()


def set_up_py_samp():
    call_native_function("CA_Init")

    streamer_set_visible_items(-1, 1000)
    pystreamer_register_callbacks()
    register_callback("OnPlayerFinishedDownloading", "ii")
    register_callback("OnPlayerRequestDownload", "iii")
    register_callback("OnCheatDetected", "isii")


def __server_timer():
    set_world_time(datetime.now().hour)


def __fractured_server_timer():
    global SERVER_GLOBAL_TIMER
    SERVER_GLOBAL_TIMER = set_timer(__server_timer, 60 * 1000, True)
    
    set_world_time(datetime.now().hour)


def __load_default_db_records():
    SkinDB.init_defaults()
    FineTypeDB.init_defaults()
    FractionDB.init_defaults()
    RoleDB.init_defaults()
    ReportCategoryDB.init_defaults()
    BusinessTypeDB.init_defaults()
    CommandDB.init_defaults()
    CommandPermissionDB.init_defaults()
    FuelTypeDB.init_defaults()
    PlayerDB.init_defaults()
    HouseTypeDB.init_defaults()
    VehicleModelDB.init_defaults()
    HouseDB.init_defaults()
    BusinessDB.init_defaults()
    VehicleColorDB.init_defaults()
    ItemDB.init_defaults()
    RankDB.init_defaults()

def __clear_player_in_game_ids():
    with transactional_session(MAIN_SESSION) as session:
        players = session.scalars(select(PlayerDB)).all()

        for player in players:
            player.in_game_id = -1


def load_teleports():
    pass


def load_telco_towers():
    with MAIN_SESSION() as session:
        telco_towers = session.query(TelCoTowerDB).all()

        for telco_tower in telco_towers:
            zone = DynamicZone.create_circle(telco_tower.x, telco_tower.y, telco_tower.radius, world_id=0, interior_id=0)
            telco_tower.in_game_id = zone.id

        session.commit()


def load_frequencies():
    with MAIN_SESSION() as session:
        frequencies = session.query(FrequencyDB).all()

        for frequency in frequencies:
            FREQUENCIES[frequency.number] = frequency
            FREQUENCY_PLAYERS[frequency.number] = []


def load_duty_locations():
    with MAIN_SESSION() as session:
        duty_locations = session.query(DutyLocationDB).all()

        for duty_location in duty_locations:

            zone: DutyPointDynamicZone = DutyPointDynamicZone.create_sphere(duty_location.x, duty_location.y, duty_location.z, duty_location.size, world_id=duty_location.virtual_word, interior_id=duty_location.interior)

            DutyPointDynamicZone.add_registry_item(zone.id, zone)

            zone.duty_point = DutyLocation(duty_location.id, duty_location.x, duty_location.y, duty_location.z, duty_location.size, duty_location.virtual_word, duty_location.interior, Transform.get_dto(FractionDB, FractionDTO, duty_location.fraction_id), zone.id)
            duty_location.in_game_id = zone.id

        session.commit()


def load_interiors():
    with transactional_session(MAIN_SESSION) as session:
        interiors = session.query(InteriorDB).all()

        for interior in interiors:
            x, y, z, a = float(interior.x), float(interior.y), float(interior.z), float(interior.a)
            interior_id: int = interior.interior

            zone: InteriortDynamicZone = InteriortDynamicZone.create_sphere(x, y, z, 1.0, interior_id=interior_id)
            
            InteriortDynamicZone.add_registry_item(zone.id, zone)

            business_type: BusinessTypeDTO = Transform.convert_db_to_dto(interior.business_type, BusinessTypeDTO)

            interior_srv: Interior = Interior(interior.id, x, y, z, a, interior_id, interior.price, business_type, zone)
            interior_srv.zone.interior = interior_srv


def load_custom_skins():
    with transactional_session(MAIN_SESSION) as session:
        stmt = select(SkinDB).filter((SkinDB.dff_path != None) & (SkinDB.txd_path != None))
        skins: list[SkinDB] = list(session.scalars(stmt).all())

        for skin in skins:
            call_native_function("AddCharModel", skin.base_id, skin.gta_id, f"{skin.dff_path}.dff", f"{skin.txd_path}.txd")
