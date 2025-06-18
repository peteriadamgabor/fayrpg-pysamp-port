import atexit
import json
import os

from pysamp.object import Object
from pysamp import call_native_function

from pystreamer.dynamicobject import DynamicObject
from python.utils.vars import GATES
from python.model.server import GateObject, Gate, Map, Model

from config import settings


def init_module():
    print(f"Module {__name__} is being initialized.")
    
    load_maps()


def load_maps():
    base_path = settings.paths.MAPS

    map_dirs = [
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d)) and not d.startswith("_")
    ]

    for map_dir in map_dirs:
        OBJECT_FILE_NAMES = ["objects.json", "object_pack_1.json", "object_pack_2.json", "object_pack_3.json", "interior.json", "exterior.json"]
        REMOVE_FILE_NAMES = ["remove.json", "remove_building.json"]
        GET_FILE_NAMES = ["gates.json", "gate.json"]

        map = Map()
        dir_path = os.path.join(base_path, map_dir)

        map_files = [
            f for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f))
        ]

        metadata_file = next(
            (f for f in ["metadata.json", "descriptor.json"] if f in map_files),
            None
        )

        if not metadata_file:
            continue

        with open(os.path.join(dir_path, metadata_file)) as f:
            file_content = json.load(f)
            map.name = file_content.get("name", "")
            map.description = file_content.get("description", "")
            map.author = file_content.get("author", "")
            map.created = file_content.get("created", "")
            map.position = tuple(file_content.get("position", ()))
            map.is_active = file_content.get("is_active", True)

            if not map.is_active:
                continue

            OBJECT_FILE_NAMES.extend(file_content.get("object_files", []))
            REMOVE_FILE_NAMES.extend(file_content.get("remove_object_files", []))
            GET_FILE_NAMES.extend(file_content.get("gate_files", []))

            if "models" in file_content:
                map.models.extend(Model(**model) for model in file_content["models"])

            for model in map.models:
                base_id: int = model.base_id
                new_id: int = model.new_id
                dff: str = f"objects/{model.dff}"
                txd: str = f"objects/{model.txd}"

                call_native_function("AddSimpleModel", -1, base_id, new_id, dff, txd)

        map_files.remove(metadata_file)

        try:
            for map_file in map_files:
                full_path = os.path.join(dir_path, map_file)
                with open(full_path) as f:
                    file_content = json.load(f)

                if map_file in OBJECT_FILE_NAMES:
                    for f_object in file_content:
                        __create_object(f_object, map)

                elif map_file in REMOVE_FILE_NAMES:
                    map.remove_objects.extend(
                        (
                            f_object["model_id"],
                            f_object["x"],
                            f_object["y"],
                            f_object["z"],
                            f_object["radius"],
                        )
                        for f_object in file_content
                    )

                elif map_file in GET_FILE_NAMES:
                    for gate in file_content:
                        __create_gate(gate, map)

                else:
                    Logger.write_log(f"Unknown map file {map_file} in {map_dir}")

        except Exception as ex:
            print(f"ERROR IN LOAD MAP!! NAME: {map.name} !!!")
            print(ex)

        Map.add_registry_item(map.name, map)

def __create_gate(gate, map):
    py_gate = Gate(
        speed=gate.get("speed"),
        auto=gate.get("auto"),
        close_time=gate.get("close_time"),
    )

    for gate_object in gate.get("objects", []):
        py_gate_object = GateObject(
            gate_object["model_id"],
            gate_object["x"],
            gate_object["y"],
            gate_object["z"],
            gate_object["rotation_x"],
            gate_object["rotation_y"],
            gate_object["rotation_z"],
            gate_object.get("world_id", 0),
            gate_object.get("interior_id", 0),
            gate_object.get("draw_distance", 0),
            gate_object.get("stream_distance", 0),
            gate_object.get("move_x", 0),
            gate_object.get("move_y", 0),
            gate_object.get("move_z", 0),
            gate_object.get("move_rotation_x", 0),
            gate_object.get("move_rotation_y", 0),
            gate_object.get("move_rotation_z", 0),
        )

        py_gate_object.create_object()
        py_gate.objects.append(py_gate_object)

    GATES.append(py_gate)
    map.gates.append(py_gate)


def __create_object(f_object, map):
    if f_object.get("static", False):
        s_object = Object.create(
            int(f_object["model_id"]),
            float(f_object["x"]),
            float(f_object["y"]),
            float(f_object["z"]),
            float(f_object["rotation_x"]),
            float(f_object["rotation_y"]),
            float(f_object["rotation_z"]),
        )
        map.static_objects.append(s_object)

    else:
        d_object = DynamicObject.create(
            int(f_object["model_id"]),
            float(f_object["x"]),
            float(f_object["y"]),
            float(f_object["z"]),
            float(f_object["rotation_x"]),
            float(f_object["rotation_y"]),
            float(f_object["rotation_z"]),
            world_id=f_object.get("world_id", 0),
            interior_id=f_object.get("interior_id", 0),
            draw_distance=f_object.get("draw_distance", 0.0),
            stream_distance=f_object.get("stream_distance", 3000.0),
        )
        
        for material in f_object.get("materials", []):
            d_object.set_material(
                int(material["material_index"]),
                int(material["model_id"]),
                material["txd_name"],
                material["texture_name"],
                int(material.get("material_color", 0), 0),
            )

        for material_text in f_object.get("material_texts", []):
            d_object.set_material_text(
                material_text["material_index"],
                material_text["text"],
                material_text["material_size"],
                material_text["font_face"],
                material_text["font_size"],
                material_text["bold"],
                material_text["font_color"],
                material_text["back_color"],
                material_text["text_alignment"]
            )
        
        map.dynamic_objects.append(d_object)


def unload_module():
    print(f"Module {__name__} is being unloaded.")
    

atexit.register(unload_module)

init_module()

from . import commands
