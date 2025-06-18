from python.utils.enums.colors import Color
from python.model.server import Player
from python.model.server import Vehicle
from python.utils.enums.fractrion_types import FractionTypes
from python.utils.decorator import cmd_arg_converter
from python.utils.enums.translation_keys import TranslationKeys
from pystreamer.dynamicobject import DynamicObject
from pysamp import call_native_function

@Player.command(aliases=("jaror",))
@Player.using_registry
def patrol(player: Player, *name: str) -> None:

	if player.fraction.type != FractionTypes.LAW_ENFORCEMENT:
		player.send_message_multi_lang(Color.ORANGE, "Nem vagy a megfelelő frakcióban")
		return

	if not player.in_duty:
		player.send_message_multi_lang(Color.ORANGE, "Nem vagy a szolgálatban!")
		return

	veh: Vehicle | None = player.get_vehicle()

	if veh is None:
		player.send_message_multi_lang(Color.ORANGE, "Nem ültsz a megfelelő járműben!")
		return

	concat_name = " ".join(name)

	if concat_name in player.fraction.patrols:
		player.send_system_message_multi_lang(Color.ORANGE, "Ez a hívójel már foglalt! ")
		return

	result = veh.set_patrol(*name)

	if result == 0:
		player.send_system_message_multi_lang(Color.GREEN, "Kikapcsoltad a járőr helyzetmegjelölést!")
		player.fraction.send_msg(f"{player.name} a {veh.plate} forgalmi rendszámű járőrautóval befejezte a járőrt")

	elif result == 1:
		player.send_system_message_multi_lang(Color.GREEN, f"Sikeresen beállítottad a járőr helyzetmegjelölést {concat_name} néven!")
		player.fraction.send_msg(f"{player.name} a {veh.plate} forgalmi rendszámű járőrautóval járőrbe kezdett.\nA járőregység hívójele: {concat_name}\nTagok: {", ".join([i.name for i in veh.passengers])}")

	elif result == 2:
		player.send_system_message_multi_lang(Color.ORANGE, f"Nem adtál meg járőr nevet!")

	else:
		pass


@Player.command(aliases=("blokad",))
@Player.using_registry
@cmd_arg_converter
def blockade(player: Player, btype: int, otype: int = -1 ) -> None:

	if player.fraction.type != FractionTypes.LAW_ENFORCEMENT:
		return

	if btype is str:
		player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
		return

	if  btype < 1 or btype > 5:
		player.send_system_message_multi_lang(Color.ORANGE, "Érvénytelen típus: 1, 2, 3, 4")
		return

	if btype == 5:
		if otype is str or otype == -1:
			player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTANUMBER)
			return

	model_id = 0

	match btype:
		case 1:
			model_id = 2899
		case 2:
			model_id = 981
		case 3:
			model_id = 978
		case 4:
			model_id = 3578
		case 5:
			model_id = otype
		case _:
			model_id = 978

	x, y, z = player.get_pos()
	a = player.get_facing_angle()

	blockade_object: DynamicObject = DynamicObject.create(model_id, x, y, z,0, 0, a, 0, 0)

	player.set_pos(x, y, z + 4)
	player.send_message_multi_lang(Color.GREEN, "Leraktál egy blokádot!")
	player.send_message_multi_lang(Color.GREEN, "Ha el akarod töntetni: /blokad torol!")
	player.make_action("lerakott egy blokádot!")

	player.fraction.blockades.append(blockade_object)


