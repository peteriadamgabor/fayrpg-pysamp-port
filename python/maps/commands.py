
from pysamp.object import Object
from pystreamer.dynamicobject import DynamicObject
from python.admin.functions import check_player_role_permission, send_admin_action

from python.dialogtree import DialogTree
from python.dialogtree import ActionNode
from python.dialogtree import ListNode

from python.model.server import Player
from python.model.server.map import Map

from python.utils.enums.colors import Color

@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def listmaps(player: Player):
    root_node: ListNode = ListNode("maps_root", "Név\tstatic\tdynamic\tremove\n", "Kiválaszt", "Bezár", "Mappolások", True, True)
    tree: DialogTree = DialogTree()
    root_node.set_tree(tree)
    tree.add_root(root_node)

    for key, map in Map.get_registry_items_with_keys():
        display: str = f"{key}\t{len(map.static_objects)}\t{len(map.dynamic_objects)}\t{len(map.remove_objects)}"
        teleport_content: str = f"x: {map.position[0]} | y: {map.position[1]} | z: {map.position[2]} | int: {map.position[3]} | vw: {map.position[4]}"
        
        map_node: ListNode = ListNode("maps_root", "", "Kiválaszt", "Bezár", f"{key} - Mappolás adatai", display=display)
        map_node.set_tree(tree)

        teleport_node: ActionNode = ActionNode("teleport_node", teleport_content)
        teleport_node.response_handler = teleport_to_object
        teleport_node.response_handler_parameters = map.position[0], map.position[1], map.position[2], map.position[3], map.position[4],
        teleport_node.close_in_end = True
        teleport_node.set_tree(tree)

        unload_node: ActionNode = ActionNode("unload_node", "Unload")
        unload_node.response_handler = unload_map
        unload_node.response_handler_parameters = key,
        unload_node.close_in_end = True
        unload_node.set_tree(tree)
        
        map_node.add_child(teleport_node)
        map_node.add_child(unload_node)

        objects_node: ListNode = ListNode("maps_root", "", "Kiválaszt", "Bezár", f"{key} - Mappolás Objectek", display="Objectek")
        objects_node.set_tree(tree)

        for i in map.static_objects:
            obj: Object = i

            x, y, z = obj.get_position()

            teleport_object_node: ActionNode = ActionNode("teleport_node", f"Static: 1 | Model Id: {obj.get_model():<6} | x: {x:.4f} | y: {y:.4f} | z: {z:.4f} | int: -1 | vw: -1")
            teleport_object_node.response_handler = teleport_to_object
            teleport_object_node.response_handler_parameters = x, y, z, 0, 0
            teleport_object_node.close_in_end = True
            teleport_object_node.set_tree(tree)

            objects_node.add_child(teleport_object_node)

        for i in map.dynamic_objects:
            obj: DynamicObject = i

            teleport_object_node: ActionNode = ActionNode("teleport_node", f"Static: 0 | Model Id: {obj._model_id:<6} | x: {obj._x:.4f} | y: {obj._y:.4f} | z: {obj._z:.4f} | int: {obj._interior_id} | vw: {obj._world_id}")
            teleport_object_node.response_handler = teleport_to_object
            teleport_object_node.response_handler_parameters = obj._x, obj._y, obj._z, obj._interior_id, obj._world_id
            teleport_object_node.close_in_end = True
            teleport_object_node.set_tree(tree)

            objects_node.add_child(teleport_object_node)
            
        map_node.add_child(objects_node)

        root_node.add_child(map_node)
    tree.show_root_dialog(player)

@Player.using_registry
def teleport_to_object(player: Player, response: int, list_item: int, input_text: str, *args):
    player.set_pos(float(args[0]), float(args[1]), float(args[2]))
    player.set_interior(int(args[3]) if int(args[3]) != -1 else 0)
    player.set_virtual_world(int(args[4]) if int(args[4]) != -1 else 0)

@Player.using_registry
def unload_map(player: Player, response: int, list_item: int, input_text: str, *args):
    map: Map = Map.get_registry_item(args[0])

    for i in map.dynamic_objects:
        obj: DynamicObject = i
        obj.destroy()

    for i in map.static_objects:
        obj: Object = i
        obj.destroy()

    player.send_system_message(Color.ORANGE, f"{args[0]} sikeresen kikapcsolva!")
    send_admin_action(player, f"kikapcsolva a(z) {args[0]} object munkát!")

@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def remove_obj(player: Player, model, x, y, z, r):
    player.remove_building(int(model), float(x), float(y), float(z), float(r))


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def starteditmaps(player: Player):
    player.select_object()


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
def stopeditmaps(player: Player):
    player.cancel_object_selection()
