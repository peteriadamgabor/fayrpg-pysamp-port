from python.discord import send_embed
from python.model.server import Player
from python.model.server import ReportCategory
from python.utils.enums.colors import Color


@Player.using_registry
def send_report_msg(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    category_code: str = args[0]

    if len(input_text) < 3:
        player.send_system_message(Color.ORANGE, "Túl rövid a jelentésed! Minimum 3 karakternek kell lennie!")
        return
    
    category = ReportCategory.get_registry_item(category_code)
    formatted_msg: str = f"{{{category.color}}}*JELENTÉS* *{category.code}* {player.name}[{player.id}]: {input_text}"

    send_embed(f"Jelentés a {category.code} kategóriában", f"{player.name}[{player.id}]: {input_text}", category.color, "report")

    if not ReportCategory.get_registry_item("MINDEN").admins and not ReportCategory.get_registry_item(category_code).admins:
        player.send_system_message(Color.ORANGE, "Jelenleg nincs elérhető admin! De továbbításra került Discordra!")
        return

    if len(formatted_msg) > 144:
        player.send_system_message(Color.ORANGE, "Nem fog kiférni az egész jelentésed egy sorban! Fogalmazz rövidebben vagy küld el több részletben!")
        return

    player.send_system_message(Color.YELLOW, f"A kavetkezo jelentésed sikeresen elküldve az adminoknak az adott kategóriában:\n*{category_code}*: {input_text}")

    for admin in ReportCategory.get_registry_item("MINDEN").admins.values():
        admin.send_client_message(Color.WHITE, formatted_msg)

    for admin in ReportCategory.get_registry_item(category_code).admins.values():
        admin.send_client_message(Color.WHITE, formatted_msg)

    return


@Player.using_registry
def send_report_emergency(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):

    msg_a = f"*JELENTÉS VÉSZHELYZET* {player.name}[{player.id}] azonnali TV-zést igényel!"
    msg_p = f"*JELENTÉS* Az adminok értesítésre kerültek! Hamarosan reagálnak!"

    send_embed(f"VÉSZHELYZET", f"{player.name}[{player.id}] vészhelyzetett jelentett!", "FF0000", "report")

    for lplayer in Player.get_registry_items():

        if lplayer.role is None:
            continue

        if lplayer.role:
                lplayer.send_client_message(Color.JB_RED, msg_a)

    lplayer.send_client_message(Color.JB_RED, msg_p)
    return


@Player.using_registry
def change_admin_category(player: Player, response: int, list_item: int, input_text: str, category_code: str, *args, **kwargs):
    category: ReportCategory | None = ReportCategory.get_registry_item(category_code)
    in_category: ReportCategory | None = player.report_category

    if category is None or in_category is None:
        print("ERROR IN change_admin_category")
        return

    category.admins[player.id] = player
    in_category.admins.pop(player.id, None)
    player.report_category = category

    if category_code == "AFK":
        player.send_system_message(Color.GREEN, f"Mostantól nem fogsz egy jelentéset se kapni!")

    else:
        player.send_system_message(Color.GREEN, f"Mostantól {{{category.color}}}{category_code}{{33AA33}} katergória jelentéseit fogod látni!")
