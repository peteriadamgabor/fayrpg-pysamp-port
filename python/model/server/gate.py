import threading
from dataclasses import dataclass, field

from python.utils.enums.gate_state import GateState
from .gate_object import GateObject
from python.model.dto import Fraction


@dataclass
class Gate:
    speed: int
    auto: bool
    close_time: int

    is_opened: bool = False

    state: GateState = GateState(0)
    fractions: list[Fraction] = field(default_factory=list)
    objects: list[GateObject] = field(default_factory=list)

    timer: threading.Timer | None = None

    def open(self):
        for gate_object in self.objects:
            gate_object.move_to_open(self.speed)

        if self.auto:
            self.timer = threading.Timer(self.close_time, self.__timed_closed)
            self.timer.start()

    def close(self):
        for gate_object in self.objects:
            gate_object.move_to_close(self.speed)

    def __timed_closed(self):
        for gate_object in self.objects:
            gate_object.move_to_close(self.speed)

        if self.timer:
            self.timer.cancel()
            self.timer = None
