import random

from python.model.server import Player

from ..functions import generate_points


@Player.command
@Player.using_registry
def searchground(player: Player):
    index: int | None = player.custom_vars.get("closest_detector_index", None)

    if index is not None:
        item_id: int = random.randint(1, 15)
        matches = [random.randint(1, 15) for _ in range(6)]

        if item_id in matches:
            player.send_client_message(-1, f"Nem találtált semmit.") 

        else:
            player.send_client_message(-1, f"Egy itemet") 

        del player.custom_vars["detector_pos"][index]

        player.custom_vars["detector_pos"].extend(generate_points(player, 1, 45))

    else:
        player.send_client_message(-1, f"Nem vagy elég közel a ponthoz") 
