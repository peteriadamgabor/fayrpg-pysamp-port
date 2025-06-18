from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from pysamp.player import Player
from pysamp.playertextdraw import PlayerTextDraw


@dataclass
class PlayerVariable:
    dbid: int
    is_registered: bool
    login_date: datetime

    is_recording: bool = False
    block_for_pickup: bool = False
    used_teleport: bool = False
    in_duty: bool = False
    in_duty_point: bool = False
    is_dead: bool = False
    set_to_back: bool = False
    current_check_point_index: int = 0
    frequency: int = -1
    dead_by_weapon_id: int = 0
    fps: int = 30
    current_drunk: int = 0
    hospital_release_date: datetime = datetime.now() - timedelta(hours=1)
    

    timers: dict[str, int] = field(default_factory=dict)
    markers: list[tuple[tuple[float, float, float], int, int]] = field(default_factory=lambda: [(0.0, 0.0, 0.0), 0, 0] * 100)
    damages: dict[int, list[Any]] = field(default_factory=lambda: {3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []})
    in_hand_weapons: dict[int, int] = field(default_factory=lambda: {0: -1, 1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1, 8: -1, 9: -1, 10: -1, 11: -1, 12: -1, 13: -1})
    text_draws: dict[str, list[PlayerTextDraw]] = field(default_factory=dict)
    dialog_vars: dict[str, Any] = field(default_factory=dict)
    check_points: list[Any] = field(default_factory=list)
    houses: list = field(default_factory=list)
    custom_vars: dict[str, Any] = field(default_factory=dict)
    streamed_players: list[Any] = field(default_factory=list)
    streamed_vehicles: list[Any] = field(default_factory=list)
    active_zones: list[Any] = field(default_factory=list)
    ac_warns: dict[str, int] = field(default_factory=lambda: {"ping": 0})
    ac_detection: dict[str, int] = field(default_factory=lambda: { "mods": False })

@dataclass
class VehicleVariable:
    dbid: int | None

    is_starting: bool = False
    is_registered: bool = False
    skip_check_damage: bool = False

    panels_damage_bit: int = 0
    doors_damage_bit: int = 0
    lights_damage_bit: int = 0
    tires_damage_bit: int = 0

    passengers: set[Player] = field(default_factory=set)
    passenger_activity: list[str] = field(default_factory=list)
