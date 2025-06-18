import atexit

from . import detections

from .tiggers import ping, money, armour, health

from pysamp import register_callback, set_timer, kill_timer

from python.model.server import Player as PlayerSRV

TIMER: int | None = None

def __timer_job():
    try:
        for player in PlayerSRV.get_registry_items():
            pass
            #ping.tigger(player)
            #money.tigger(player)
            #health.tigger(player)
            #armour.tigger(player)

    except Exception as e:
        raise e


def init_module():
    global TIMER 

    print(f"Module {__name__} is being initialized.")

    register_callback("OnOldVersionDetected", "i")
    register_callback("OnImprovedDeagleDetected", "i")
    register_callback("OnExtraWsDetected", "i")
    register_callback("OnS0beitDetected", "i")
    register_callback("OnSampfuncsDetected", "i")
    register_callback("OnSprintHookDetected", "i")
    register_callback("OnModsDetected", "i")
    register_callback("OnBypassDetected", "i")
    register_callback("OnSilentAimDetected", "i")

    TIMER = set_timer(__timer_job, 5000, True)

def unload_module():
    global TIMER 

    print(f"Module {__name__} is being unloaded.")

    if TIMER is not None:
        kill_timer(TIMER)


atexit.register(unload_module)

init_module()




