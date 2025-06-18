import random

from pysamp import set_timer
from pystreamer.dynamictextlabel import DynamicTextLabel
from python.model.server import Player
from python.utils.enums.colors import Color

from ..functions import generate_points

@Player.command
@Player.using_registry
def detector(player: Player):
    how_many: int = random.randint(4, 15)

    detector_pos: list[(float, float)] = generate_points(player, how_many, 60)

    player.custom_vars["detector_pos"] = detector_pos
    player.timers["check_detector"] = set_timer(check_detector_dist, 1500, True, player)
    player.timers["play_detector_sound"] = set_timer(play_detector_sound, 1750, True, player)


def check_detector_dist(player: Player):
    player.stop_audio_stream()
    _, _, z = player.get_pos()

    closest_index, closest_dist = -1, 9999.9

    for index, (x, y) in enumerate(player.custom_vars["detector_pos"]):
        new_dist = player.distance_from_point(x, y, z)

        if closest_dist > new_dist:
            closest_dist = new_dist
            closest_index = index
    
    player.custom_vars["closest_detector_index"] = closest_index
    player.custom_vars["closest_detector_dist"] = closest_dist
    

def play_detector_sound(player: Player):
 
    closest_dist: float = player.custom_vars["closest_detector_dist"]
 
    if closest_dist < 5.0:
        player.play_sound(1139,0.0,0.0,0.0)
        set_timer(player.play_sound, 500, False, 1139, 0.0, 0.0, 0.0)
        set_timer(player.play_sound, 750, False, 1139, 0.0, 0.0, 0.0)
        set_timer(player.play_sound, 1000, False, 1139, 0.0, 0.0, 0.0)

    elif closest_dist < 15.0:
        player.play_sound(1138, 0.0, 0.0, 0.0)
        set_timer(player.play_sound, 500, False, 1138, 0.0, 0.0, 0.0)
    
    elif closest_dist < 25.0:
        player.play_sound(1137, 0.0, 0.0, 0.0)