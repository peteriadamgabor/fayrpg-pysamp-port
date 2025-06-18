from pydantic import BaseModel as PydanticModel

import datetime

from .skin import Skin as SkinDTO

class PlayerParameter(PydanticModel):
   fraction_skin: SkinDTO | None
   payment: int | None
   today_played: int | None
   hospital_time: int | None
   food_time: datetime.datetime
   job_lock_time: datetime.datetime
   is_over_limit: bool | None
   is_leader: bool | None
   is_division_leader: bool  | None
   fine: int  | None
   deaths: int  | None