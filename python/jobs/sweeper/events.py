from python.model.server import Player
from python.utils.enums.colors import Color


def job_sweeper_on_enter_checkpoint(player: Player):
    if not player.in_vehicle(574):
        return

    next_index = player.custom_vars["sweeper_job"]
    pos_list = player.custom_vars["sweeper_pos"]
    next_index += 1

    if next_index >= len(pos_list):
        player.send_system_message(Color.GREEN, f"Véget ért az útvonalad! A pénz jóváírva a fizetésedhez!")
        player.add_payment(player.custom_vars["sweeper_pay"])
        del player.custom_vars["sweeper_job"]
        del player.custom_vars["sweeper_pos"]
        del player.custom_vars["sweeper_pay"]
        return

    pos_json = pos_list[next_index]
    player.custom_vars["sweeper_job"] = next_index
    player.set_checkpoint(pos_json["x"], pos_json["y"], pos_json["z"], size=5)
