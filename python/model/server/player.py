import datetime
import math
import re
from functools import singledispatch
from typing import Any, Callable, Optional, Union, override

from sqlalchemy import select, delete

from pysamp import get_player_animation_index, kill_timer, set_timer, get_vehicle_z_angle, call_native_function
from pysamp.dialog import Dialog
from pysamp.event import event
from pysamp.player import Player as BasePlayer
from pysamp.playertextdraw import PlayerTextDraw
from pystreamer.dynamicmapicon import DynamicMapIcon
from pystreamer import update_ex as streamer_update_ex
from pystreamer import update as streamer_update

from python.model.attribute_monitor import AttributeMonitor
from python.model.registrymixin import RegistryMixin
from python.utils.enums.states import State
from python.utils.helper.function import get_skin_id, get_weapon_slot
from python.utils.helper.item import is_stackable_item
from python.utils.helper.python import fixchars, format_numbers, round_to_nearest_hundred, get_uuid7

from python.language import get_translated_text
from python.database import transactional_session 

from python.utils.enums.colors import Color

from python.server.database import PLAYER_SESSION

from python.model.transorm import Transform
from python.model.variable import PlayerVariable

from python.model.database import Player as PlayerDB
from python.model.database import Skin as SkinDB
from python.model.database import Fraction as FractionDB
from python.model.database import Rank as RankDB
from python.model.database import InventoryItem as InventoryItemDB
from python.model.database import House as HouseDB
from python.model.database import Role as RoleDB
from python.model.database import Division as DivisionDB

from python.model.dto import Skin as SkinDTO
from python.model.dto import Role as RoleDTO
from python.model.dto import PlayerParameter as PlayerParameterDTO
from python.model.dto import Fraction as FractionDTO
from python.model.dto import Division as DivisionDTO
from python.model.dto import Rank as RankDTO
from python.model.dto import InventoryItem as InventoryItemDTO

from .house import House
from .report_category import ReportCategory
from .vehicle import Vehicle as VehicleSRV

from python.utils.enums.text_draw_align import TextDrawAlign

from python.utils.helper.math import is_point_in_ashlar


class Player(BasePlayer, RegistryMixin[int, "Player"], AttributeMonitor):

    @classmethod
    def fiend(cls, search_value: str | int) -> Optional["Player"]:
        if type(search_value) is int or search_value.isdigit():  # type: ignore
            return cls.get_registry_item(int(search_value))
        else:
            return next((p for p in cls.get_registry_items() if search_value.lower() in p.get_name().lower()), None)  # type: ignore

    @classmethod
    def is_existing(cls, search_value: str | int):
        return cls.fiend(search_value) is None

    def __init__(self, player_id: int):
        super().__init__(player_id) # Initialize BasePlayer
        AttributeMonitor.__init__(self, None, {"session_token", "today_played",  } ) # Initialize AttributeMonitor
    
        self.is_logged_in: bool = False
        self.language: str = "hu"
        self._variables: PlayerVariable | None = None
        self.dbid: int = -1
        self.password: str = "N/A"
        self.money: int = 0
        self.job: int = -1
        self.sex: int = 0
        self.played_time: int = 0
        self.birthdate: datetime.date = datetime.datetime.fromisoformat("1899-01-01")
        self.skin: SkinDTO | None = None
        self.role: RoleDTO | None = None
        self._parameter: PlayerParameterDTO | None = None
        self.fraction: FractionDTO | None = None
        self.division: DivisionDTO | None = None
        self.rank: RankDTO | None = None
        self.session_token: str = "session_token is missing"
        self.last_state: State = State.NONE
        self.is_action_locked: bool = False
        self.report_category = None
        self.map_icons: dict[str, list[DynamicMapIcon]] = {}
        self.__update_ctn = 0

    def init(self) -> bool:
        with transactional_session(PLAYER_SESSION) as session:
            stmt = select(PlayerDB).where(((PlayerDB.in_game_id == self.id) | (PlayerDB.name == self.get_name())) & (PlayerDB.is_activated == 1))
            player_obj = session.scalars(stmt).first()

            if not player_obj:
                return False

            self._variables = PlayerVariable(player_obj.id, True, datetime.datetime.now())

            self.dbid = player_obj.id
            self.password = player_obj.password
            self.money = player_obj.money
            self.job = player_obj.job_id
            self.skin = Transform.convert_db_to_dto(player_obj.skin, SkinDTO)
            self.sex = player_obj.sex
            self.played_time = player_obj.played_time
            self.birthdate = player_obj.birthdate
            self.role = Transform.convert_db_to_dto(player_obj.role, RoleDTO, True)
            self._parameter = Transform.convert_db_to_dto(player_obj.parameter, PlayerParameterDTO, True)
            self.fraction = FractionDTO.get_registry_item(player_obj.fraction_id)
            self.division = DivisionDTO.get_registry_item(player_obj.division_id)
            self.rank = RankDTO.get_registry_item(player_obj.rank_id)

            if player_obj.parameter is not None and player_obj.parameter.hospital_time > 0:
                hospital_time = player_obj.parameter.hospital_time
                self.variables.hospital_release_date = datetime.datetime.now() + datetime.timedelta(0, hospital_time)
               
            self.timers["update_database_entity"] = set_timer(self.update_database_entity, 60000, True)
            self.timers["streamer_update"] = set_timer(self.update_streamer_object,  2 * 1000, True)
            self.is_logged_in: bool = True

            if self.role is not None:
                report_category: ReportCategory = ReportCategory.get_registry_item("MINDEN")
                self.report_category = report_category
                report_category.admins[self.id] = self

            self.__set_skills()
            self.load_items()
            self.set_drunk_level(2000)
            self.set_health(player_obj.health if player_obj.health > 0 else 100.0)

            self.session_token = get_uuid7()

            return True

    @override
    def update_database_entity(self, is_force_update: bool=False) -> None:
        self.__update_ctn += 1

        if not self.attr_change and not is_force_update and self.__update_ctn < 5:
            return

        if self.__update_ctn >= 5:
            self.__update_ctn = 0

        try:
            with transactional_session(PLAYER_SESSION) as session:
                player_db = session.scalars(select(PlayerDB).where(PlayerDB.id == self.dbid)).one()

                player_db.money = self.money
                player_db.job_id = self.job
                player_db.sex = self.sex
                player_db.played_time = self.played_time
                player_db.birthdate = self.birthdate
                player_db.health = self.health
                player_db.money = self.money

                player_db.skin = Transform.get_db(SkinDB, getattr(self.skin, 'id', None), existing_session=session)
                player_db.role = Transform.get_db(RoleDB, getattr(self.role, 'id', None), existing_session=session)
                player_db.fraction = Transform.get_db(FractionDB, getattr(self.fraction, 'id', None), existing_session=session)
                player_db.division = Transform.get_db(DivisionDB, getattr(self.division, 'id', None), existing_session=session)
                player_db.rank = Transform.get_db(RankDB, getattr(self.rank, 'id', None), existing_session=session)

                if self._parameter is None:
                    raise Exception("Update player error!")

                player_db.parameter.fraction_skin = Transform.get_db(SkinDB, getattr(self.parameter.fraction_skin, 'id', None), existing_session=session)
                player_db.parameter.payment = self.payment
                player_db.parameter.today_played = self.today_played 
                player_db.parameter.is_over_limit = self.is_over_limit 
                player_db.parameter.is_leader = self.parameter.is_leader if self.parameter.is_leader is not None else False
                player_db.parameter.is_division_leader  = self.parameter.is_division_leader if self.parameter.is_division_leader is not None else False
                player_db.parameter.deaths  = self.parameter.deaths if self.parameter.deaths is not None else 0
                player_db.parameter.food_time  = self.parameter.food_time
                player_db.parameter.job_lock_time  = self.parameter.job_lock_time

                if self.have_hospital_time:
                    player_db.parameter.hospital_time = (self.hospital_release_date - datetime.datetime.now()).total_seconds()
                else:
                    player_db.parameter.hospital_time = 0

        except Exception as e:
            print(e)
            pass

        finally:
            self.attr_change = False


    def update_streamer_object(self):
        streamer_update(self.id)


    # region Property
    @property
    def name(self):
        return self.get_name().replace("_", " ")

    @property
    def lvl(self) -> int:
        return self.get_score()
    
    @property
    def is_aiming(self) -> bool:
        return get_player_animation_index(self.id) in [220, 1160, 1161, 1162, 1163, 1167, 1365, 1453, 1643]

    @property
    def health(self) -> float:
        return self.get_health()
    
    @health.setter
    def health(self, hp: float | int) -> None:
        self.set_health(float(hp))
        
    @property
    def armour(self) -> float:
        return self.get_armour()
   
    @armour.setter
    def armour(self, armour: float | int) -> None:
        self.set_armour(float(armour))

    @property
    def x(self) -> float:
        return self.get_pos()[0]
    
    @property
    def y(self) -> float:
        return self.get_pos()[1]
    
    @property
    def z(self) -> float:
        return self.get_pos()[2]
    
    @property
    def a(self) -> float:
        return self.get_facing_angle()
    
    @property
    def interior(self) -> int:
        return self.get_interior()
    
    @interior.setter
    def interior(self, interior: int) -> None:
        self.set_interior(interior)

    @property
    def virtual_world(self) -> int:
        return self.get_virtual_world()

    @virtual_world.setter
    def virtual_world(self, virtual_world: int) -> None:
        self.set_virtual_world(virtual_world)

    @lvl.setter
    def lvl(self, value):
        self.set_score(value)

    @property
    def variables(self) -> PlayerVariable | None:
        if self._variables is None:
            raise Exception("Player is not inited!")
        
        return self._variables

    @property
    def parameter(self) -> PlayerParameterDTO:
        if self._parameter is None:
            raise Exception("Player is not inited!")
        
        return self._parameter

    @property
    def login_date(self):
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.login_date

    @login_date.setter
    def login_date(self, value: datetime.datetime) -> None:
        if not self.parameter or self.parameter.payment is None:
            return
        self.variables.login_date = value

    @property
    def payment(self) -> int:
        if not self.parameter or self.parameter.payment is None:
           return -1
       
        return self.parameter.payment

    @payment.setter
    def payment(self, value: int) -> None:
        if not self.parameter or self.parameter.payment is None:
            return
         
        self.parameter.payment += value

    @property
    def in_duty(self) -> bool:
        if not self.variables or self.variables.in_duty is None:
            return False

        return self.variables.in_duty

    @in_duty.setter
    def in_duty(self, value: bool) -> None:
        if not self.variables or self.variables.in_duty is None:
            return
        
        self.variables.in_duty = value

    @property
    def in_duty_point(self) -> bool:
        if not self.variables or self.variables.in_duty_point is None:
            return False
        
        return self.variables.in_duty_point

    @in_duty_point.setter
    def in_duty_point(self, value: bool) -> None:
        if not self.variables or self.variables.in_duty_point is None:
            return
        
        self.variables.in_duty_point = value

    @property
    def markers(self) -> list[tuple[tuple[float, float, float], int, int]]:
        if not self.variables or self.variables.markers is None:
            return []
         
        return self.variables.markers

    @property
    def today_played(self) -> int:
        if not self.parameter or self.parameter.today_played is None:
            return 0

        return self.parameter.today_played

    @today_played.setter
    def today_played(self, value) -> None:
        if not self.parameter or self.parameter.today_played is None:
            return

        self.parameter.today_played = value

    @property
    def hospital_time(self) -> int:
        if not self.parameter or self.parameter.hospital_time is None:
            return 0

        return self.parameter.hospital_time

    @hospital_time.setter
    def hospital_time(self, value)-> None:
        if not self.parameter or self.parameter.hospital_time is None:
            return 

        self.parameter.hospital_time = value

    @property
    def is_registered(self):
        if not self.variables or self.variables.is_registered is None:
            return None
        
        return self.variables.is_registered

    @property
    def streamed_players(self) -> list["Player"]:
        if self.is_logged_in and self.variables:
            return self.variables.streamed_players        
        
        return []

    @property
    def streamed_vehicles(self) -> list["VehicleSRV"]:
        if self.variables is None:
            raise Exception("Player is not inited!")
            
        return self.variables.streamed_vehicles

    @property
    def is_dead(self) -> bool:
        if not self.variables or self.variables.is_dead is None:
            raise Exception("Player is not inited!")
         
        return self.variables.is_dead

    @is_dead.setter
    def is_dead(self, value)-> None:
        if not self.variables or self.variables.is_dead is None:
            raise Exception("Player is not inited!")
        
        self.variables.is_dead = value

    @property
    def timers(self) -> dict[str, int]:
        if not self.variables or self.variables.timers is None:
            raise Exception("Player is not inited!")
         
        return self.variables.timers

    @property
    def text_draws(self) -> dict[str, list[PlayerTextDraw]]:
        if self.variables is None:
            raise Exception("Player is not inited!")


        return self.variables.text_draws

    @property
    def check_points(self) -> list[Any]:
        if self.variables is None:
            raise Exception("Player is not inited!")
         
        return self.variables.check_points

    @property
    def dialog_vars(self):
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.dialog_vars

    @property
    def custom_vars(self):
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.custom_vars

    @property
    def is_recording(self):
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.is_recording

    @is_recording.setter
    def is_recording(self, value: bool) -> None:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        self.variables.is_recording = value

    @property
    def set_to_back(self):
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.set_to_back

    @set_to_back.setter
    def set_to_back(self, value: bool) -> None:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        self.variables.set_to_back = value

    @property
    def hospital_release_date(self) -> datetime.datetime:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.hospital_release_date

    @hospital_release_date.setter
    def hospital_release_date(self, value: datetime.datetime) -> None:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        self.variables.hospital_release_date = value

    @property
    def block_for_pickup(self) -> bool:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.block_for_pickup

    @block_for_pickup.setter
    def block_for_pickup(self, value: bool) -> None:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        self.variables.block_for_pickup = value

    @property
    def is_over_limit(self) -> bool:
        if self.parameter is None or self.parameter.is_over_limit is None:
            raise Exception("Player is not inited!")
        
        return self.parameter.is_over_limit

    @is_over_limit.setter
    def is_over_limit(self, value: bool) -> None:
        if self.parameter is None:
            raise Exception("Player is not inited!")
        
        self.parameter.is_over_limit = value

    @property
    def dead_by_weapon_id(self) -> int:
        if self.variables is None or self.variables.dead_by_weapon_id is None:
            raise Exception("Player is not inited!")
        
        return self.variables.dead_by_weapon_id

    @dead_by_weapon_id.setter
    def dead_by_weapon_id(self, value: int) -> None:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        self.variables.dead_by_weapon_id = value

    @property
    def current_drunk(self) -> int:
        if self.variables is None or self.variables.current_drunk is None:
            raise Exception("Player is not inited!")
        
        return self.variables.current_drunk

    @current_drunk.setter
    def current_drunk(self, value: int) -> None:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        self.variables.current_drunk = value

    @property
    def used_teleport(self) -> bool:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.used_teleport

    @used_teleport.setter
    def used_teleport(self, value: bool) -> None:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        self.variables.used_teleport = value

    @property
    def in_hand_weapons(self) -> dict[int, int]:
        if self.variables is None:
            raise Exception("Player is not inited!")
        
        return self.variables.in_hand_weapons

    @property
    def have_hospital_time(self) -> bool:
        return self.hospital_release_date is not None and self.hospital_release_date > datetime.datetime.now()

    # endregion Property

    # region Functions

    def __set_skills(self):
        self.set_skill_level(0, 800)
        self.set_skill_level(1, 999)
        self.set_skill_level(2, 999)
        self.set_skill_level(3, 999)
        self.set_skill_level(4, 800)
        self.set_skill_level(5, 999)
        self.set_skill_level(6, 800)
        self.set_skill_level(7, 999)
        self.set_skill_level(8, 999)
        self.set_skill_level(9, 999)
        self.set_skill_level(10, 800)

    def add_payment(self, value):
            calculated = value
            
            if self.payment >= 150_000:
                    if not self.is_over_limit:
                        self.is_over_limit = True
                        self.send_system_message(Color.WHITE, "Túllépted a napi fizetési limitet!")
                        self.send_system_message(Color.WHITE, "Ezért csak a fizetés 15%%-át kapod!")
                    calculated = int(value * 0.15)
            self.payment += value

            self.send_system_message(Color.GREEN, f"{format_numbers(calculated)} Ft jóváírva a fizetésedhez!")

    def load_items(self):
        with transactional_session(PLAYER_SESSION) as session:
            stmt = select(InventoryItemDB).where(InventoryItemDB.player_id == self.dbid)
            items = session.scalars(stmt).all()

            self.items: list[InventoryItemDTO] = Transform.convert_db_to_dto(items, InventoryItemDTO, True)

    def kick_with_reason(self, reason: str, public=True) -> None:
        self.send_client_message(Color.RED, reason)
        self.kick()

    def get_vehicle(self):
        return VehicleSRV.get_registry_item(int(self.get_vehicle_id()))

    def in_vehicle(self, model_id: int = -1) -> bool:
        veh = VehicleSRV.get_registry_item(int(self.get_vehicle_id()))

        if veh is None:
            return False

        if model_id == -1:
            return veh.db_id is not None

        return veh is not None and veh.get_model() == model_id

    def set_back_pos(self, given_pos: tuple[float, float, float] | None = None, given_interior: int | None = None, given_vw: int | None = None, given_a: int | None = None):
        pos: tuple[float, float, float] = self.get_pos() if given_pos is None else given_pos
        p_interior: int = self.get_interior() if given_interior is None else given_interior
        p_vw: int = self.get_virtual_world() if given_vw is None else given_vw
        p_a: float = self.get_facing_angle() if given_a is None else given_a

        self.set_to_back = True
        self.custom_vars["back_pos"] = (pos, p_interior, p_vw, p_a)

    def back(self):
        if "back_pos" in self.custom_vars:
            self.set_to_back = False
            (x, y, z) = self.custom_vars["back_pos"][0]
            interior: int = self.custom_vars["back_pos"][1]
            vw: int = self.custom_vars["back_pos"][2]
            a: float = self.custom_vars["back_pos"][3]

            self.set_pos(float(x), float(y), float(z))
            self.set_interior(int(interior))
            self.set_virtual_world(int(vw))
            self.set_facing_angle(a)

    def show_dialog(self, dialog: Dialog):
        dialog.show(self)

    def get_x_y_in_front_of(self, distance: float) -> tuple[float, float]:
        (x, y, _) = self.get_pos()
        a = self.get_facing_angle()

        if self.is_in_any_vehicle():
            a = get_vehicle_z_angle(self.get_vehicle_id())

        x = x + (distance * math.sin(math.radians(-a)))
        y = y + (distance * math.cos(math.radians(-a)))

        return x, y

    def is_block_pickup_pickup(self) -> bool:
        if self.block_for_pickup or self.is_action_locked:
            return True

        self.block_for_pickup = True
        set_timer(self.enable_pickup, 1000 * 12, False)
        return False

    def disable_pickup(self) -> None:
        self.block_for_pickup = True
        set_timer(self.enable_pickup, 1000 * 6, False)

    def check_used_teleport(self) -> bool:
        if self.used_teleport or self.is_action_locked:
            return True

        self.used_teleport = True
        set_timer(self.enable_use_teleport, 1000 * 6, False)
        return False

    def disable_teleport(self) -> None:
        self.used_teleport = True
        set_timer(self.enable_use_teleport, 1000 * 6, False)

    def transfer_money(self, money: int, target: Optional["Player"] = None) -> bool:
        if self.money < money:
            self.send_system_message(Color.RED, "Nincs elég pénzed!")
            return False

        self.money -= money

        if target:
            target.money += money
            target.send_system_message(Color.GREEN, f"{self.name} átadott neked {money} Ft-ot.")

        return True

    def hide_game_text(self, style):
        call_native_function("HideGameTextForPlayer", self.id, style)

    def calculate_hopital_fine(self):
        return round_to_nearest_hundred(
            (15_000 * (self.lvl * .25) + 0 * 150 * self.lvl) + ((self.dead_by_weapon_id + 1) * 25))

    def send_system_message(self, color: Color, msg: str) -> None:
        rows: list[str] = msg.split('\n')
        for row in rows:
            self.send_client_message(color, "(( " + row + " ))")

    def send_system_message_multi_lang(self, color: Color, msg_key: str, *args) -> None:
        rows: list[str] = get_translated_text(msg_key, self.language, *args).split('\n')

        for row in rows:
            self.send_client_message(color, "(( " + row + " ))")


    def send_message_multi_lang(self, color: Color, msg_key: str, *args) -> None:
        rows: list[str] = get_translated_text(msg_key, self.language, *args).split('\n')

        for row in rows:
            self.send_client_message(color, row)


    def broadcast_system_message(self, color: Color, msg: str, disct: float) -> None:
        self.send_client_message(color, "(( " + msg + " ))")
        for player in self.streamed_players:

            if self.in_player_distance(player, disct):
                player.send_client_message(color, "(( " + msg + " ))")

    def broadcast_chat_message(self, color: Color, msg: str, disct: float) -> None:

        emoji_msg: str = self.handle_emoji(msg)
        suffix: str = ": "

        if not emoji_msg:
            return
        
        elif "~" in emoji_msg:
            splited = emoji_msg.split("~")
            suffix = f" *{splited[0].replace("~", "")}*: "
            msg =  f"{splited[1]}"

        self.set_chat_bubble(msg, color, disct, len(msg) * 250)
        self.send_client_message(color, "Te" + suffix + msg)

        for player in self.streamed_players:
            if self.in_player_distance(player, disct):
                player.send_client_message(color, f"{self.name} " + msg)

    def broadcast_action_message(self, color: Color, msg: str, disct: float = 7.0) -> None:
        self.set_chat_bubble("*" + msg + "*", color, disct, len(msg) * 1000)
        self.send_client_message(color, f"* {self.name} {msg}")
        
        for player in self.streamed_players:
            
            if self.in_player_distance(player, disct):
                player.send_client_message(color, f"* {self.name} {msg}")

    def make_action(self, msg: str) -> None:
        self.broadcast_action_message(Color.PURPLE, msg + '.', 30.0)

    def in_player_distance(self, target: "Player", disct: float) -> bool:
        x1, y1, z1 = self.get_pos()
        x2, y2, z2 = target.get_pos()
        return math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2) + pow(z2 - z1, 2) * 1.0) <= disct

    def in_distance(self, x2: float, y2: float, z2: float, disct: float) -> bool:
        x1, y1, z1 = self.get_pos()
        return math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2) + pow(z2 - z1, 2) * 1.0) <= disct

    def get_skin_id(self):
        if self.skin is None:
            return self.get_skin()

        return get_skin_id(self.skin.id)

    def get_houses(self) -> list[House]:
         with transactional_session(PLAYER_SESSION) as session:
            houses = session.scalars(select(HouseDB).where(HouseDB.owner_id == self.dbid)).all()

            return [House.get_registry_item(house.id) for house in houses]
         
    def get_spawn_hous(self) -> House | None:
         with transactional_session(PLAYER_SESSION) as session:
            house = session.scalars(select(HouseDB).where((HouseDB.owner_id == self.dbid) & (HouseDB.is_spawn == True))).one_or_none()

            if house is None: 
                return None 

            return House.get_registry_item(house.id)

    def clear_spawn_house(self) -> None:
         with transactional_session(PLAYER_SESSION) as session:
            houses = session.scalars(select(HouseDB).where((HouseDB.owner_id == self.dbid) & (HouseDB.is_spawn == True))).all()

            for house in houses:
                house.is_spawn = False

    def show_speedo(self):
        speed_bg: PlayerTextDraw = PlayerTextDraw.create(self, 572.000, 332.000, 'LD_SPAC:white')
        speed_bg.text_size(46.000, 89.000)
        speed_bg.alignment(TextDrawAlign.TEXT_DRAW_ALIGN_LEFT)
        speed_bg.color(200)
        speed_bg.set_shadow(0)
        speed_bg.set_outline(0)
        speed_bg.background_color(255)
        speed_bg.font(4)
        speed_bg.set_selectable(True)

        speed: PlayerTextDraw = PlayerTextDraw.create(self, 576.000, 337.000, '0')
        speed.letter_size(0.180, 1.600)
        speed.alignment(TextDrawAlign.TEXT_DRAW_ALIGN_LEFT)
        speed.color(-1)
        speed.set_shadow(0)
        speed.set_outline(1)
        speed.background_color(150)
        speed.font(2)
        speed.set_proportional(True)

        speed_unit: PlayerTextDraw = PlayerTextDraw.create(self, 595.000, 337.000, 'km/h')
        speed_unit.letter_size(0.180, 1.600)
        speed_unit.alignment(TextDrawAlign.TEXT_DRAW_ALIGN_LEFT)
        speed_unit.color(-1)
        speed_unit.set_shadow(0)
        speed_unit.set_outline(1)
        speed_unit.background_color(150)
        speed_unit.font(2)
        speed_unit.set_proportional(True)

        fuel_level: PlayerTextDraw = PlayerTextDraw.create(self, 576.000, 320.000, '')
        fuel_level.letter_size(0.280, 9.3)
        fuel_level.alignment(TextDrawAlign.TEXT_DRAW_ALIGN_LEFT)
        fuel_level.color(16711935)
        fuel_level.set_shadow(1)
        fuel_level.set_outline(-1)
        fuel_level.background_color(150)
        fuel_level.font(2)
        fuel_level.set_proportional(True)

        fuel_type: PlayerTextDraw = PlayerTextDraw.create(self, 609.000, 359.000, '')
        fuel_type.letter_size(0.300, 1.6)
        fuel_type.alignment(TextDrawAlign.TEXT_DRAW_ALIGN_LEFT)
        fuel_type.color(6553855)
        fuel_type.set_shadow(1)
        fuel_type.set_outline(-1)
        fuel_type.background_color(150)
        fuel_type.font(2)
        fuel_type.set_proportional(True)

        travel_dist: PlayerTextDraw = PlayerTextDraw.create(self, 576.000, 381.000, '0 km')
        travel_dist.letter_size(0.150, 1.5)
        travel_dist.alignment(TextDrawAlign.TEXT_DRAW_ALIGN_LEFT)
        travel_dist.color(-1)
        travel_dist.set_shadow(0)
        travel_dist.set_outline(1)
        travel_dist.background_color(150)
        travel_dist.font(2)
        travel_dist.set_proportional(True)

        transmittion: PlayerTextDraw = PlayerTextDraw.create(self, 578.000, 400.000, 'R ~p~N ~w~D')
        transmittion.letter_size(0.300, 1.5)
        transmittion.alignment(TextDrawAlign.TEXT_DRAW_ALIGN_LEFT)
        transmittion.color(-1)
        transmittion.set_shadow(1)
        transmittion.set_outline(1)
        transmittion.background_color(150)
        transmittion.font(2)
        transmittion.set_proportional(True)

        speed_bg.show()
        speed.show()
        speed_unit.show()
        fuel_level.show()
        fuel_type.show()
        travel_dist.show()
        transmittion.show()

        self.text_draws["speedo"] = [speed_bg, speed, speed_unit, fuel_level, fuel_type, travel_dist, transmittion]

    def destroy_speedo(self) -> None:
        if "speedo" in self.text_draws:
            for i in self.text_draws["speedo"]:
                i.destroy()
            
            self.text_draws.pop("speedo")

    def update_speedo_trans(self, trans: str) -> None:
        if "speedo" in self.text_draws:
            speed_txd: PlayerTextDraw = self.text_draws["speedo"][6]
            speed_txd.set_string(trans)

    def update_speedo_speed(self, speed: int) -> None:
        if "speedo" in self.text_draws:

            veh: VehicleSRV = self.get_vehicle()

            if veh.limiter != 0 and veh.limiter > speed:
                speed = int(veh.limiter)

            speed_txd: PlayerTextDraw = self.text_draws["speedo"][1]
            speed_txd.set_string(str(speed))

    def update_speedo_fuel_level(self, fuel_level: int) -> None:
        if "speedo" in self.text_draws:
            if fuel_level >= 5:
                color = 16711935
            elif fuel_level >= 3:
                color = -69465615
            else:
                color = -16776961

            fuel_level = fuel_level if fuel_level > 10 else 10

            speed_txd: PlayerTextDraw = self.text_draws["speedo"][3]
            speed_txd.set_string("-" * fuel_level)
            speed_txd.color(color)

    def update_speedo_dist(self, dist: int) -> None:
        if "speedo" in self.text_draws:
            speed_txd: PlayerTextDraw = self.text_draws["speedo"][5]
            speed_txd.set_string(str(dist)+ " km")
    
    def update_speedo_fuel_type(self, type_str: str) -> None:
        if "speedo" in self.text_draws:
            speed_txd: PlayerTextDraw = self.text_draws["speedo"][4]
            speed_txd.set_string(type_str)

    #region Inventory / items

    @singledispatch
    def have_item(self, item_name: str, amount: int = 0):
        if amount > 0:
            return any(inv_item.item.name == item_name and inv_item.amount >= amount for inv_item in self.items)
        return any(inv_item.item.name == item_name for inv_item in self.items)

    @have_item.register(int)
    def _(self, item_id: int, amount: int = 0) -> bool:
        if amount > 0:
            return any(inv_item.item.id == item_id and inv_item.amount >= amount for inv_item in self.items)
        return any(inv_item.item.id == item_id for inv_item in self.items)

    def get_item(self, item_id: int) -> InventoryItemDTO | None:
        next((item.item.id == item_id for item in self.items), None)

    def give_item(self, item_id: int, amount: int) -> None:
        with transactional_session(PLAYER_SESSION) as session:
                
            if is_stackable_item(item_id) and self.have_item(item_id):
                inv_item: InventoryItemDB | None = session.scalars(select(InventoryItemDB).where((InventoryItemDB.player_id == self.dbid) & (InventoryItemDB.item_id == item_id))).first()

                if inv_item is None:
                    raise Exception("Illegal statement")

                if inv_item.item.max_amount >=  inv_item.amount + amount:
                    inv_item.amount += amount
                    self.load_items()
                    return

        InventoryItemDB.create(self.dbid, item_id, amount)
        self.load_items()

    def remove_item(self, inventory_item_id: int, amount: int = -1) -> None:
        with transactional_session(PLAYER_SESSION) as session:
            if amount == -1:
                session.execute(delete(InventoryItemDB).where(InventoryItemDB.id == int(inventory_item_id)))
            else:
                inv_item: InventoryItemDB | None = session.scalars(select(InventoryItemDB).where(InventoryItemDB.id == int(inventory_item_id))).first()

                if inv_item is None:
                    raise Exception("Illegal statement")

                if inv_item.amount - amount == 0:
                    session.execute(delete(InventoryItemDB).where(InventoryItemDB.id == int(inventory_item_id)))
                else:
                    inv_item.amount -= amount
        self.load_items()

    def transfer_item(self, target_player: "Player", inv_item_id: int, amount: int, robbing: bool = False) -> None:
        with transactional_session(PLAYER_SESSION) as session:
            src_inv_item: InventoryItemDB | None = session.scalars(select(InventoryItemDB).where((InventoryItemDB.player_id == self.dbid) & (InventoryItemDB.id == inv_item_id))).first()
            
            if src_inv_item is None:
                    raise Exception("Illegal statement")
            
            item_id: int = src_inv_item.item.id

            if is_stackable_item(item_id) and target_player.have_item(item_id):
                target_inv_items: list[InventoryItemDB] = list(session.scalars(select(InventoryItemDB).where((InventoryItemDB.player_id == target_player.dbid) & (InventoryItemDB.item_id == item_id))).all())

                for target_inv_item in target_inv_items:
                    if target_inv_item.item.max_amount >= target_inv_item.amount + amount:
                        target_inv_item.amount += amount
                        break

                else:
                    InventoryItemDB.create(target_player.dbid, item_id, amount)
                    
                if src_inv_item.amount - amount == 0:
                    self.remove_item(src_inv_item.id)
                else:
                    self.remove_item(src_inv_item.id, amount)
                    
        self.load_items()
        target_player.load_items()

    #endregion Inventory / items

    def calculate_lvl(self, hours: int) -> int:
        if not hours:
            return 1

        exp = hours
        level_exp = 4
        lvl_xp = level_exp * 2
        lvl = 1

        while exp >= lvl_xp:
            lvl += 1
            exp -= lvl_xp
            lvl_xp += level_exp

        return lvl

    def get_nearest_vehicle(self, check_distance: float = 5.0, model_id: int = 0) -> VehicleSRV | None:
        dist = 99999.98
        nearest_vehicle = None
        p_x, p_y, p_z = self.get_pos()

        for check_vehicle in VehicleSRV.get_registry_items():
            if model_id == 0 or check_vehicle.get_model() == model_id:
                new_dist = check_vehicle.get_distance_from_point(p_x, p_y, p_z)

                if dist > new_dist:
                    dist = new_dist
                    nearest_vehicle = check_vehicle

        if dist <= check_distance:
            return nearest_vehicle
        
        return nearest_vehicle

    def get_nearest_vehicles(self, check_distance: float = 5.0, model_id: int = 0) -> list[VehicleSRV]:
        p_x, p_y, p_z = self.get_pos()

        result = []

        for check_vehicle in VehicleSRV.get_registry_items():
            if check_vehicle and (model_id == 0 or check_vehicle.get_model() == model_id):
                dist = check_vehicle.get_distance_from_point(p_x, p_y, p_z)

                if check_distance >= dist:
                    result.append(check_vehicle)
    
        return result 

    def count_near_by_players(self, check_distance: float = 5.0) -> int:
        cnt = 0

        for i in self.streamed_players:
            if self.distance_from_point(i.x, i.y, i.z) >= check_distance:
               cnt += 1

        return cnt

    def get_nearest_player(self, check_distance: float = 5.0):
        nearest_player = self.streamed_players[0] if len(self.streamed_players) > 0 else None
        start_index: int = 0 if nearest_player is None else 1
        dist = 0.0

        if nearest_player:
            n_x, n_y, n_z = nearest_player.get_pos()
            dist = self.distance_from_point(n_x, n_y, n_z)

        for check_player in self.streamed_players[start_index:]:
            if check_player:
                n_x, n_y, n_z = check_player.get_pos()
                new_dist = self.distance_from_point(n_x, n_y, n_z)

                if dist > new_dist:
                    dist = new_dist
                    nearest_player = check_player

        if dist <= check_distance:
            return nearest_player
        return None

    def is_in_ashlar(self, x1, y1, z1, x2, y2, z2):
        xs, ys, zs = self.get_pos()
        return is_point_in_ashlar(xs, ys, zs, x1, y1, z1, x2, y2, z2)

    def get_distance_from_point(self, point2):
        x1, y1, z1 = self.get_pos()
        x2, y2, z2 = point2

        distance = math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2) + pow(z2 - z1, 2) * 1.0)
        return distance

    def kill_timers(self):
        for _, timer_id in self.timers.items():
            kill_timer(timer_id)

    def kill_timer(self, timer_name):
        exist_timer: int | None = self.timers.get(timer_name, None)

        if exist_timer is not None:
            kill_timer(exist_timer)

    def add_timer(self, timer_name: str,  function: Callable, tiem_in_sec: float, repeating: bool, *args: tuple):
        exist_timer: int | None = self.timers.get(timer_name, None)

        if exist_timer is not None:
            kill_timer(exist_timer)

        self.timers[timer_name] = set_timer(function, int(tiem_in_sec * 1_000), repeating, *args)

    def change_skin(self, skin_id: int) -> bool:
        with PLAYER_SESSION() as session:
            skin: SkinDB | None = session.query(SkinDB).filter(SkinDB.id == skin_id).first()

            if not skin:
                return False

            self.skin = Transform.get_dto(SkinDB, SkinDTO, skin.id)
            super().set_skin(get_skin_id(skin.id))

            self.update_database_entity(True)

        return True

    def enable_pickup(self):
        self.block_for_pickup = False

    def enable_use_teleport(self):
        self.used_teleport = False

    def eat_food(self, size: int):
        if self.parameter.food_time - datetime.timedelta(minutes=15) > datetime.datetime.now():
            self.send_system_message_multi_lang(Color.ORANGE, f"Túletted magad! Ezért rosszul lettél")
            self.health = self.health - (self.health * 0.375)
            self.make_action("elkezd hányni.")
            self.apply_animation("FOOD", "EAT_Vomit_P", 4.1, False, False, False, False, 0, True)
            return

        if self.health <= 25:
            self.health = self.health + (35 * (size / 10) + size)

        elif self.health <= 45:
            self.health = self.health + (55 * (size / 10) + size)

        elif self.health <= 65:
            self.health = self.health + (75 * (size / 10) + size)

        self.parameter.food_time = self.parameter.food_time + datetime.timedelta(minutes= (13.3 * size) + 1 )
        self.apply_animation("FOOD", "EAT_Burger", 4.1, False, False, False, False, 0, True)
        self.update_database_entity(True)

    def start_action(self, animation_library: str, animation_name: str, loop_anim: bool, game_text: str, time: int, action_msg: str, function: Callable, *args: tuple):
        if self.is_action_locked:
            return

        self.is_action_locked = True
        timer_time = time * 1_000

        self.make_action(action_msg)
        self.game_text(game_text, timer_time, 3)
        self.apply_animation(animation_library, animation_name, 4.1, loop_anim, False, False, True, 0, True)

        self.add_timer("clear_player_action_anim", self.__clear_player_action_anim, time, False)
        self.add_timer("player_action_timer", function, time, False, *(self, *args))


    def __clear_player_action_anim(self):
        self.clear_animations(True)
        self.is_action_locked = False


    # endregion

    # region Helpers

    def handle_emoji(self, msg: str) -> str:
        
        match msg.upper():
            case ":D" | ":D" | ":-D" | ":Đ":
                self.make_action("nevet")
                return ""
            case "XD":
                self.make_action("röhög")
                return ""
            case ":S" | ":-S":
                self.make_action("rosszul lesz")
                return ""
            case ":)" | ":]" | ":-)":
                self.make_action("mosolyog")
                return ""
            case ":(" | ":-(":
                self.make_action("szomorú")
                return ""
            case ":P":
                self.make_action("nyelvet ölt")
                return ""
            case ":'(":
                self.make_action("sír")
                return ""
            case ";)":
                self.make_action("kacsint")
                return ""
            case ":O":
                self.make_action("csodálkozik")
                return ""
            case ":$":
                self.make_action("elpirul")
                return ""
            case ":@":
                self.make_action("mérges")
                return ""
        
        if any([emoji in msg.upper() for emoji in [":D", ":D", ":-D", ":Đ"]]):
            return  "nevetve~" + re.sub(":D|:d|:-D|:-d|:Đ", "", msg)
        
        if any([emoji in msg.upper() for emoji in ["XD"]]):
            return  "röhögve~" + re.sub("XD|Xd|xD|xd", "", msg)
        
        if any([emoji in msg.upper() for emoji in [":)", ":]", ":-)"]]):
            return  "mosolyogva~" + re.sub(r":\)|:]|:-\)", "", msg)
        
        if any([emoji in msg.upper() for emoji in [":(", ":-("]]):
            return  "szomorúan~" + re.sub(r":\(|:-\(", "", msg)
        
        if any([emoji in msg.upper() for emoji in [":'("]]):
            return  "sírva~" + re.sub(r":'\(", "", msg)

        if any([emoji in msg.upper() for emoji in [":O"]]):
            return  "csodálkozva~" + re.sub(":O|:o", "", msg)
        
        if any([emoji in msg.upper() for emoji in [":@"]]):
            return  "mérgesen~" + re.sub(":@", "", msg)
        
        if any([emoji in msg.upper() for emoji in [":$"]]):
            return  "meghatódva~" + re.sub(":$", "", msg)

        return msg

    # endregion

    # region Overrides

    @override
    def set_drunk_level(self, level: int) -> bool:
        self.current_drunk = level
        return super().set_drunk_level(level)

    @override
    def kick(self):
        set_timer(super().kick, 1000, False)

    @override
    def set_health(self, health: float):
        if not self.is_logged_in:
            return
        
        with transactional_session(PLAYER_SESSION) as session:
            player_model: PlayerDB = session.scalars(select(PlayerDB).where(PlayerDB.id == self.dbid)).one()
            player_model.health = health
            super().set_health(health)

    @override
    def set_armour(self, armour: float) -> bool:
        return super().set_armour(armour)

    @override
    def set_skin(self, skinid: int) -> bool:
        with transactional_session(PLAYER_SESSION) as session:
            skin: SkinDB | None = session.query(SkinDB).filter((SkinDB.id - 1) == skinid).first()
            if not skin:
                return False

            super().set_skin(get_skin_id(self.skin.id))

        return True

    @override
    def set_pos(self, x: float, y: float, z: float) -> bool:
        ret = super().set_pos(x, y, z)
        self.set_camera_behind()
        return ret

    @override
    def game_text(self,msg,time,style) -> bool:
        return super().game_text(fixchars(msg),time,style)

    @override
    def give_weapon(self, weapon_id: int, ammo: int) -> bool:
        slot_id = get_weapon_slot(weapon_id)

        if slot_id is None:
            return False

        self.in_hand_weapons[slot_id] = weapon_id
        return super().give_weapon(weapon_id, ammo)

    @override
    def send_client_message(self, color: Color, msg: str) -> None:
        rows: list[str] = msg.split('\n')
        for row in rows:
            super().send_client_message(color, row)

    # endregion

    # region Events

    @classmethod
    @event("OnPlayerRequestDownload")
    def request_download(cls, player_id: int, type: int, crc):
        return cls(player_id), type, crc # type: ignore

    @classmethod
    @event("OnPlayerFinishedDownloading")
    def finished_downloading(cls, player_id: int, virtualworld: int):
        return cls(player_id), virtualworld # type: ignore
    
    # region AC 

    @classmethod
    @event("OnOldVersionDetected")
    def old_version_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore

    @classmethod
    @event("OnImprovedDeagleDetected")
    def improved_deagle_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore

    @classmethod
    @event("OnExtraWsDetected")
    def extra_ws_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore

    @classmethod
    @event("OnS0beitDetected")
    def s0beit_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore

    @classmethod
    @event("OnSampfuncsDetected")
    def samp_funcs_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore
    
    @classmethod
    @event("OnSprintHookDetected")
    def sprint_hook_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore

    @classmethod
    @event("OnModsDetected")
    def mods_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore
    
    @classmethod
    @event("OnBypassDetected")
    def bypass_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore
    
    @classmethod
    @event("OnSilentAimDetected")
    def silent_aim_detected(cls, player_id: int):
        return (cls(player_id), ) # type: ignore

    #endregion AC 


    @classmethod
    @event("OnPlayerSelectObject")
    @override
    def on_select_object(
        cls,
        playerid: int,
        type: int,
        objectid: int,
        modelid: int,
        x: float,
        y: float,
        z: float,
    ):
        return (
            cls(playerid), # type: ignore
            type,
            objectid,
            modelid,
            x,
            y,
            z,
        )

    # endregion

    #region OpenMP

    def is_using_omp(self) -> bool:
        return call_native_function("IsPlayerUsingOmp", self.id)

    def select_object(self) -> None:
        return call_native_function("BeginObjectSelecting", self.id)
    
    def edit_object(self, object_id: int) -> None:
        return call_native_function("BeginObjectEditing", self.id, object_id)
    
    def cancel_object_selection(self) -> None:
        return call_native_function("EndObjectEditing", self.id)
    
    def remove_weapon(self, weapon_id: int):
        slot_id = get_weapon_slot(weapon_id)

        if slot_id is None:
            return None

        self.in_hand_weapons[slot_id] = -1
        return call_native_function("RemovePlayerWeapon", self.id, weapon_id)

    def get_position(self) -> tuple[float, float, float]:
        return super().get_pos()

    # endregion

    # region Registry
    
    @classmethod
    def from_registry(cls, player_: Union[BasePlayer, int]) -> Union["Player", None]:
        player_id: int | None = None  # Initialize player_id to None

        if isinstance(player_, int):
            player_id = player_

        if isinstance(player_, BasePlayer):
            player_id = player_.id

        if player_id is None:
            raise Exception()

        ret_player: Player | None = cls._registry.get(player_id)

        if not ret_player:
            cls._registry[player_id] = ret_player = cls(player_id)

        return ret_player

    def get_id(self) -> int:
        return self.id

    # endregion

  