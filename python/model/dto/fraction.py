import itertools

from typing import Optional, Any
from pydantic import BaseModel as PydanticModel

from python.model.registrymixin import RegistryMixin
from python.utils.enums.colors import Color

from .skin import Skin as SkinDTO
from .rank import Rank as RankDTO
from .division import Division as DivisionDTO


class Fraction(PydanticModel, RegistryMixin[int, "Fraction"]):
    id: int
    name: str
    acronym: str
    duty_everywhere: int
    duty_players: list[Any] = []
    calls: dict[int, tuple[Any, tuple[float, float, float]]] = {}
    skins: list[SkinDTO] | None
    #duty_points: list["DutyLocationDTO"] | None
    divisions: list[DivisionDTO] | None
    ranks: list[RankDTO] | None
    type: Optional[int]
    patrols: list[str] = []
    blockades: list[Any] = []

    __id_iter = itertools.count(1)

    def model_post_init(self, __context):
        self.add_registry_item(self.id, self)


    def get_id(self) -> int:
        return self.id


    def add_new_call(self, player, location) -> int:
        call_id: int = next(self.__id_iter)
        self.calls[call_id] = (player, location)
        return call_id


    def send_system_msg(self, msg: str, *args) -> None:
        for player in self.duty_players:
            player.send_system_message_multi_lang(Color.LIGHTBLUE, msg, *args)


    def send_msg(self, msg: str, *args) -> None:
        for player in self.duty_players:
            player.send_message_multi_lang(Color.LIGHTBLUE, msg, *args)
