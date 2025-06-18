from sqlalchemy import select
from pyeSelect.eselect import Menu, MenuItem

from python.database.context_managger import transactional_session

from python.model.server import Business, Player, Interior, Vehicle

from python.model.database import Player as PlayerDB
from python.model.database import Interior as InteriorDB
from python.model.database import RestaurantMenu as RestaurantMenuDB
from python.model.database import VehicleModel as VehicleModelDB
from python.model.database import VehicleColor as VehicleColorDB
from python.model.database import Vehicle as VehicleDB
from python.model.database import FuelType as FuelTypeDB

from python.model.dto import Player as PlayerDTO
from python.model.dto import Interior as InteriorDTO
from python.model.dto import RestaurantMenu as RestaurantMenuDTO

from python.model.transorm import Transform

from python.server.database import BUSINESS_SESSION, VEHICLE_SESSION
from python.utils.enums.colors import Color
from python.utils.enums.translation_keys import TranslationKeys
from python.utils.globals import BUESSNES_VIRTUAL_WORD
from python.utils.helper.python import format_numbers

from python.dialogtree.dialog_tree import DialogTree
from python.dialogtree.nodes.action import ActionNode
from python.dialogtree.nodes.list import ListNode
from python.dialogtree.nodes.message import MessageNode
from python.utils.vars import VEHICLE_PLATE_MAP


@Player.using_registry
def buy_business(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    business: Business = args[0]

    if not player.transfer_money(business.price):
        return

    player.send_system_message(Color.GREEN, f"Sikeresen megvetted a(z) {{AA3333}}{business.name}{{33AA33}} bizniszt!")
    business.owner = Transform.get_dto(PlayerDB, PlayerDTO, player.dbid)


@Player.using_registry
def lock_business(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    business: Business | None = Business.get_registry_item(int(args[0].id))

    if not business:
        return

    if business.locked:
        player.send_system_message(Color.GREEN, "Sikeresen kinyitottad a bizniszt")
        business.locked = False

    else:
        player.send_system_message(Color.GREEN, "Sikeresen bezártad a bizniszt")
        business.locked = True


@Player.using_registry
def sell_business(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    business: Business = args[0]

    business.owner = None

    player.send_system_message(Color.GREEN, "Sikeresen eladtad a bizniszt!")
    player.money += int(business.price * .75)


@Player.using_registry
def enter_business(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    business: Business = args[0]

    if business.locked:
        player.send_system_message(Color.RED, "Zárva van!")
        return
    
    if not business.interior:
        player.send_system_message(Color.RED, "Ebbe az épületbe nem lehet belépni!")
        return

    player.disable_teleport()
    
    player.set_pos(business.interior.x, business.interior.y, business.interior.z)
    player.set_facing_angle(business.interior.a if business.interior.a else 0.0)

    player.set_interior(business.interior.interior)
    player.set_virtual_world(BUESSNES_VIRTUAL_WORD + business.id)


@Player.using_registry
def change_business_interior(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    business: Business | None = Business.get_registry_item(int(args[0]))
    interior: Interior | None = Interior.get_registry_item(int(args[1]))

    if not interior or not business:
        player.send_system_message(Color.RED, "HIBA!")
        return

    interior_dto: InteriorDTO | None = InteriorDTO.get_registry_item(int(args[1]))

    is_business_int_none = business.interior is None

    if not interior_dto:
        business.interior = Transform.get_dto(InteriorDB, InteriorDTO, interior.id)
    
    else:
        business.interior = interior_dto

    if is_business_int_none:
        player.send_system_message(Color.GREEN, "Mivel eddig nem volt az üzlethelység berendezve ezért ez a művelet nem került pézbe!")
        return
    
    if not player.transfer_money(interior.price):
        return
        
    player.send_system_message(Color.GREEN, f"Új üzlet helység megvásárolva {format_numbers(interior.price)} Ft-ért!")


@Player.using_registry
def eval_menu_item_use(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs) -> None:
    business: Business | None = Business.get_registry_item(int(args[0]))
    menu_item: RestaurantMenuDTO | None = Transform.get_dto(RestaurantMenuDB, RestaurantMenuDTO, int(args[1]))

    if not menu_item or not business:
        return

    if not player.transfer_money(menu_item.price):
        return
    
    eval(menu_item.execute)


@Player.using_registry
def eval_food(player: Player, size: int) -> None:
    player.eat_food(size)


@Player.using_registry
def change_skin(player: Player, menu_item: MenuItem):

    price: int = int(menu_item.text.replace("Ft", "").strip().replace(" ", "_"))

    if not player.transfer_money(price):
        player.send_system_message_multi_lang(Color.ORANGE, TranslationKeys.NOTENOUGHMONEY)
        return

    player.change_skin(menu_item.model_id)
    player.send_system_message_multi_lang(Color.GREEN, f"Sikeresen megvetted a ruhát {menu_item.text}-ért!")


@Player.using_registry
def list_car_catalog(player: Player, response: int, list_item: int, input_text: str, business_id: int, *args, **kwargs):
    business: Business | None = Business.get_registry_item(int(business_id))

    if not business:
        return

    with transactional_session(BUSINESS_SESSION) as session:
        models: list[VehicleModelDB] = list(session.scalars(select(VehicleModelDB).where(VehicleModelDB.id.in_([i.vehicle_model_id for i in business.cars]))).all())
                                          
        menu = Menu(
            f'{business.name}',
            [MenuItem(model.id + 399, f"{format_numbers(model.price)} Ft", -15.0, 0.0, -45.0, 1) for model in models],
            on_select=show_buy_dialog,
            additional_data=(business.id,)
        )

        menu.show(player)


@Player.using_registry
def show_buy_dialog(player: Player, menu_item: MenuItem, business_id: int, *args):
    
    with transactional_session(BUSINESS_SESSION) as session:
        model: VehicleModelDB = session.scalars(select(VehicleModelDB).where(VehicleModelDB.id == menu_item.model_id - 399)).one()

        colors: list[VehicleColorDB] = list(session.scalars(select(VehicleColorDB).where(VehicleColorDB.can_paint == True)).all())

        content: str = f"{{{{FFFFFF}}}}Név: {{{{00C0FF}}}}{model.real_name} {{{{FFFFFF}}}}(({{{{00C0FF}}}}{model.name}{{{{FFFFFF}}}})){{{{00C0FF}}}}\n" \
                       f"{{{{FFFFFF}}}}Ár: {{{{00C0FF}}}}{format_numbers(model.price)} Ft\n" \
                       f"{{{{FFFFFF}}}}Ülések: {{{{00C0FF}}}}{model.seats}\n" \
                       f"{{{{FFFFFF}}}}Üzemanyag: {{{{00C0FF}}}}{",".join([ i.name for i in model.allowed_fuel_types])}\n" \
                       f"{{{{FFFFFF}}}}Tank: {{{{00C0FF}}}}{model.tank_capacity} liter\n" \
                       f"{{{{FFFFFF}}}}Fogyasztás: {{{{00C0FF}}}}{model.consumption} l/100km\n" \
                       f"{{{{FFFFFF}}}}Csomagtartó: {{{{00C0FF}}}}{model.trunk_capacity} liter\n" \
                       f"{{{{FFFFFF}}}}Szín: {{{{00C0FF}}}}{"Egyszínű" if model.color_number == 1 else "Kétszínű"}"

        root_node: MessageNode = MessageNode("root", content, "Megvesz", "Vissza", f"{model.real_name} adatai")
        tree: DialogTree = DialogTree()

        root_node.close_handler = list_car_catalog
        root_node.close_handler_parameters = (-1, -1, "", business_id)

        config_node: ListNode = ListNode("config_node", "", "Tovább", "Vissza", f"{model.real_name} konfiguráció")

        fuel_node: ListNode = ListNode("fuel_node", f"{"\n".join([ i.name for i in model.allowed_fuel_types])}", "Kiválaszt", "Vissza", f"{model.real_name} üzemanyag lista", True, display="Üzemanyag: #fuel_node.input_value#")
        fuel_node.save_input = True
        fuel_node.back_after_input = True
        
        color1_node: ListNode = ListNode("color1_node", f"{"\n".join([ i.name for i in colors])}", "Kiválaszt", "Vissza", f"{model.real_name} elsődleges színe", True, display="Elsődleges szín: #color1_node.input_value#")
        color1_node.save_input = True
        color1_node.back_after_input = True


        if model.color_number == 2:
            color2_node: ListNode = ListNode("color2_node", f"{"\n".join([ i.name for i in colors])}", "Kiválaszt", "Vissza", f"{model.real_name} elsődleges színe", True, display="Másodlagos szín: #color2_node.input_value#")
            color2_node.save_input = True
            color2_node.back_after_input = True

            config_node.add_child(color2_node)

        buy_node: ActionNode = ActionNode("buy_node", "Megvesz")
        buy_node.guard = check_is_filled
        buy_node.guard_parameters = (model.color_number, )
        buy_node.guard_node_parameters = ("fuel_node.input_value", "color1_node.input_value", "color2_node.input_value", )
        buy_node.response_handler = buy_new_car
        buy_node.response_handler_parameters = (business_id, model.id, )
        buy_node.response_handler_node_parameters = ("fuel_node.input_value", "color1_node.input_value", "color2_node.input_value", )



        config_node.add_child(fuel_node)
        config_node.add_child(color1_node)
        config_node.add_child(buy_node)

        root_node.add_child(config_node)

        tree.add_root(root_node)
        tree.show_root_dialog(player)

@Player.using_registry
def check_is_filled(player: Player, color_number: int, fuel_type: str, color1: str, color2 : str, *args):

    if color_number == 2 and (color1 == "N/A" or color2 == "N/A"):
        player.send_system_message(Color.ORANGE, "Nem választottál ki minden színt!")
        return False
    
    if  color1 == "N/A":
        player.send_system_message(Color.ORANGE, "Nem választottál ki színt!")
        return False
    
    if fuel_type == "N/A":
        player.send_system_message(Color.ORANGE, "Nem választottál ki üzemanyag típust!")
        return False
    
    return True


@Player.using_registry
def buy_new_car(player: Player, response: int, list_item: int, input_text: str, business_id: int, model_id: int, fuel_type: str, color1: str, color2: str, *args):

    new_veh_palte: str = "N/A"

    with transactional_session(BUSINESS_SESSION) as session:
        model: VehicleModelDB = session.scalars(select(VehicleModelDB).where(VehicleModelDB.id == model_id)).one()

        fine_type: FuelTypeDB = session.scalars(select(FuelTypeDB).where(FuelTypeDB.name == fuel_type)).one()

        color_1: int = session.scalars(select(VehicleColorDB).where(VehicleColorDB.name == color1)).one().id
        color_2_db: VehicleModelDB | None = session.scalars(select(VehicleColorDB).where(VehicleColorDB.name == color2)).one_or_none() # type: ignore

        color_2: int | None = color_2_db.id if color_2_db is not None else None # type: ignore

        business: Business | None = Business.get_registry_item(int(business_id))

        if not business:
            return

        if player.transfer_money(model.price):
            new_veh_plate = VehicleDB.create(model_id, business.load_x, business.load_y, business.load_z, business.load_a,
                                             color_1, color_2, fine_type.id, player.dbid, None)

    with transactional_session(VEHICLE_SESSION) as session:
        car_model: VehicleModelDB = session.scalars(select(VehicleModelDB).where(VehicleModelDB.id == model_id)).one()
        car = session.scalars(select(VehicleDB).where(VehicleDB.plate == new_veh_plate)).one()
        session.refresh(car)

        car_color_1: int = car.color_1
        car_color_2: int = car.color_2

        veh: Vehicle = Vehicle.create(car_model.id + 399, car.x, car.y, car.z, car.angle, car_color_1, car_color_2, -1, car.plate, False, car.id)
        car.in_game_id = veh.id

        VEHICLE_PLATE_MAP.setdefault(car.plate, veh)
    
        player.send_system_message_multi_lang(Color.GREEN, f"Sikeresen megvettél egy {car_model.real_name} ( {car_model.name} ) \nEnnek ára: {format_numbers(car_model.price)} Ft volt ami a pénztárcádból lett kifizetve! \nA jármű forgalmi rendszáma: {new_veh_plate}\nA megjelőlt helyen megtalálod az új járművedet!")
        player.set_checkpoint(business.load_x, business.load_y, business.load_z, 10)
