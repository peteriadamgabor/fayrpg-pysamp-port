from dataclasses import dataclass
from pystreamer.dynamicobject import DynamicObject


@dataclass
class GateObject:
    model_id: int

    x: float
    y: float
    z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float

    world_id: int
    interior_id: int
    draw_distance: float
    stream_distance: float

    move_x: float
    move_y: float
    move_z: float
    move_rotation_x: float
    move_rotation_y: float
    move_rotation_z: float

    object: DynamicObject = None

    def create_object(self):
        self.object = DynamicObject.create(self.model_id,
                                           self.x,
                                           self.y,
                                           self.z,
                                           self.rotation_x,
                                           self.rotation_y,
                                           self.rotation_z,
                                           world_id=self.world_id,
                                           interior_id=self.interior_id,
                                           draw_distance=self.draw_distance,
                                           stream_distance=self.stream_distance)

    def move_to_open(self, speed: float = 1.0):
        self.object.move(self.move_x, self.move_y, self.move_z, speed,
                         self.move_rotation_x, self.move_rotation_y, self.move_rotation_z)

    def move_to_close(self, speed: float = 1.0):
        self.object.move(self.x, self.y, self.z, speed,
                         self.move_rotation_x, self.move_rotation_y, self.move_rotation_z)