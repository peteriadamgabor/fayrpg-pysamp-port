from python.jobs.sweeper.events import job_sweeper_on_enter_checkpoint
from python.model.server import Player

@Player.on_enter_checkpoint # type: ignore
@Player.using_registry
def on_enter_checkpoint(player: Player):
    player.disable_checkpoint()
    player.play_sound(1139, 0, 0, 0)

    if "sweeper_job" in player.custom_vars:
        job_sweeper_on_enter_checkpoint(player)
        return

