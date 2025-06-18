from python.model.dto import DutyLocation
from .zone import DynamicZone

class DutyPointDynamicZone(DynamicZone):
    def __init__(self, id: int):
        super().__init__(id)
        self.__duty_point: DutyLocation | None

    @property
    def duty_point(self) -> DutyLocation:
        return self.__duty_point

    @duty_point.setter
    def duty_point(self, duty_point: DutyLocation) -> None:
        self.__duty_point = duty_point
