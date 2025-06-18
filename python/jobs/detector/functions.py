import math
import random

from pystreamer.dynamictextlabel import DynamicTextLabel
from python.model.server import Player
from python.utils.enums.colors import Color


def generate_random_point_in_circle(radius: float):
    angle = random.uniform(0, 2 * math.pi)
    
    r = radius * math.sqrt(random.uniform(0, 1))
    
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    
    return (x, y)


def generate_points(player: Player, number: int, offset_range: float) -> list[(float, float)]:
    x, y, z = player.get_pos()

    detector_pos: list[(float, float)] = []

    for i in range(number):
        offset_x, offset_y = generate_random_point_in_circle(offset_range)

        spot_x, spot_y = x + offset_x, y + offset_y
        detector_pos.append((spot_x, spot_y))

        DynamicTextLabel.create(f"|=== DETECTOR {i} ===|", Color.LABEL_RED, spot_x, spot_y, z + 1.0, 25.0)

    return detector_pos