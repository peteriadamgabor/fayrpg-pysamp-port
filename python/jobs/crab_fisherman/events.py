
from pystreamer import create_dynamic_map_icon, destroy_dynamic_map_icon
from pystreamer.dynamicmapicon import DynamicMapIcon
from python.model.server import Vehicle
from python.model.server import Player

def show_icon_cages(player: Player, vehicle: Vehicle):

    if "crab_cages" in vehicle.custom_vars:
        for i in vehicle.custom_vars["crab_cages"]:
            if i.in_water:
                i.mapicon = DynamicMapIcon.create(i.pos_x,i.pos_y,i.pos_z,19,i.id,0,0,player.id,1000.0)

def remove_icon_cages(player: Player, vehicle: Vehicle):

    if "crab_cages" in vehicle.custom_vars:
        for i in vehicle.custom_vars["crab_cages"]:
            if i.mapicon is not None:
                i.mapicon.destroy()
                i.mapicon = None