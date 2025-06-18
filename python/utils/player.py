from math import sqrt

from python.model.server import Gate, GateObject
from python.utils.vars import GATES


def get_nearest_gate(player_pos):
    if len(GATES) == 0:
        return None

    nearest_gate: Gate = GATES[0]
    dist = calculate_dist(player_pos,
                          (nearest_gate.objects[0].x, nearest_gate.objects[0].y, nearest_gate.objects[0].z))

    for gate in GATES[1:]:
        gate_object: GateObject = gate.objects[0]

        now_dist = calculate_dist(player_pos, (gate_object.x, gate_object.y, gate_object.z))

        if dist > now_dist:
            dist = now_dist
            nearest_gate = gate

    if dist <= 5.0:
        return nearest_gate
    return None


def calculate_dist(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    distance = sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2) + pow(z2 - z1, 2) * 1.0)
    return distance

