from python.model.server import House
from python.model.server import Player
from python.utils.enums.colors import Color
from python.utils.globals import HOUSE_VIRTUAL_WORD


@Player.command(aliases=("kilep",))
@Player.using_registry
def exit(player: Player):

    vw = player.get_virtual_world()

    if vw < HOUSE_VIRTUAL_WORD:
        return

    house: House = House.get_by_virtual_word(vw)

    if not house:
        return

    if house.locked:
        player.send_system_message(Color.RED, "A ház zárva van!")
        return

    if not player.is_in_range_of_point(5, house.house_type.enter_x, house.house_type.enter_y, house.house_type.enter_z):
        player.send_system_message(Color.RED, "Nem vagy az ajtónál!")
        return

    player.disable_pickup()
    player.disable_teleport()
    player.set_pos(house.entry_x, house.entry_y, house.entry_z)
    player.set_facing_angle(house.angle)
    player.set_interior(0)
    player.set_virtual_world(0)


@Player.command(aliases=("nyitzar",))
@Player.using_registry
def openlock(player: Player):

    vw = player.get_virtual_world()

    if vw < HOUSE_VIRTUAL_WORD:
        return

    house: House = House.get_by_virtual_word(vw)

    if not house:
        return

    if not player.is_in_range_of_point(5, house.house_type.enter_x, house.house_type.enter_y, house.house_type.enter_z):
        player.send_system_message(Color.RED, "Nem vagy az ajtónál!")
        return

    if house.locked:
        player.send_system_message(Color.GREEN, "Kinyitottad a házat!")
        house.locked = False

    else:
        player.send_system_message(Color.GREEN, "Bezártad a házat!")
        house.locked = True


@Player.command(aliases=("betoro",))
@Player.using_registry
def burglar(player: Player):
    vw = player.get_virtual_world()

    if vw < HOUSE_VIRTUAL_WORD:
        return

    house: House = House.get_by_virtual_word(vw)

    if not house:
        return

    if house.locked:
        player.send_system_message(Color.RED, "A ház zárva van!")
        return

    if not player.is_in_range_of_point(5, house.house_type.enter_x, house.house_type.enter_y, house.house_type.enter_z):
        player.send_system_message(Color.RED, "Nem vagy az ajtónál!")
        return

    player.disable_pickup()
    player.disable_teleport()
    player.set_pos(house.entry_x, house.entry_y, house.entry_z)
    player.set_facing_angle(house.angle)
    player.set_interior(0)
    player.set_virtual_world(0)
