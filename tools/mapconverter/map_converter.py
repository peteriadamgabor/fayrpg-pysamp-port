import csv
import datetime
import json
import re
import time
import os

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from models.material import Material
from models.metadata import Metadata
from models.object import Object
from models.remove_object import RemoveObject
from models.material_text import MaterialText

APP = typer.Typer()
OBJECTS: list[Object] = []
REMOVE_OBJECTS: list[RemoveObject] = []
METADATA: Metadata

@APP.command()
def csv_convert(file_name: str):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description="Processing...", total=None)
        __csv_convert(file_name)
        time.sleep(2)
        print("Convert is done!")


def __csv_convert(file_name: str):
    with open(f'src_csv/{file_name}.csv') as csvfile:

        reader = csv.reader(csvfile)
        next(reader, None)

        for row in reader:
            OBJECTS.append(Object(
                name="",
                model_id=int(row[3]),
                x=float(row[4]),
                y=float(row[5]),
                z=float(row[6]),
                rotation_x=float(row[7]),
                rotation_y=float(row[8]),
                rotation_z=float(row[9]),
                world_id=int(row[2]),
                interior_id=int(row[1]),
                stream_distance=float(row[10]),
                draw_distance=0.0,
                static=row[12] == '1',
                materials=[]
            ))

        dump_map(file_name)


@APP.command()
def pwn_convert(file_name: str):
    with open(f'tools/mapconverter/src_map_code/{file_name}.txt') as map_src:

        global METADATA

        prev_obj = None

        for row in map_src.readlines():
            result = re.search(r'\((.*?)\)', row)
            if not result:
                continue

            data = result.group(1).split(",")
            is_spec = False

            if "CreateDynamicObject".lower() in row.lower():

                if (world_id_str := next((i for i in data if ".worldid" in i), None)) is not None:
                    world_id = world_id_str.split("=")[1].strip()
                    is_spec = True

                if (interior_id_str := next((i for i in data if ".interiorid" in i), None)) is not None:
                    interior_id = interior_id_str.split("=")[1].strip()
                    is_spec = True

                if (stream_distance_str := next((i for i in data if ".streamdistance" in i), None)) is not None:
                    stream_distance = stream_distance_str.split("=")[1].strip()
                    is_spec = True

                world_id = 0
                interior_id = 0
                stream_distance = 300.0
                draw_distance = 0.0

                if is_spec:
                    world_id = 0 if world_id_str is None else int(world_id_str.split("=")[1].strip())
                    interior_id = 0 if interior_id_str is None else int(interior_id_str.split("=")[1].strip())
                    stream_distance = 300 if stream_distance_str is None else float(
                        stream_distance_str.split("=")[1].strip())
                    draw_distance = 0

                if len(data) == 9 and "CreateDynamicObjectEx".lower() in row.lower():
                    stream_distance = float(data[7].strip())
                    draw_distance = float(data[8].strip())

                elif len(data) == 9:
                    world_id = int(data[7].strip())
                    interior_id = int(data[8].strip())

                if len(data) == 10:
                    world_id = int(data[7].strip())
                    interior_id = int(data[8].strip())
                    stream_distance = float(data[9].strip())
                    draw_distance = float(data[10].strip())

                model_id: int = int(data[0].strip())
                x: float = float(data[1].strip())
                y: float = float(data[2].strip())
                z: float = float(data[3].strip())
                rotation_x: float = float(data[4].strip())
                rotation_y: float = float(data[5].strip())
                rotation_z: float = float(data[6].strip())
                world_id: int = world_id
                interior_id: int = interior_id
                stream_distance: float = stream_distance
                draw_distance: float = draw_distance

                prev_obj = Object(
                    name="",
                    model_id=model_id,
                    x=x,
                    y=y,
                    z=z,
                    rotation_x=rotation_x,
                    rotation_y=rotation_y,
                    rotation_z=rotation_z,
                    world_id=world_id,
                    interior_id=interior_id,
                    stream_distance=stream_distance,
                    draw_distance=draw_distance,
                    static=False,
                    materials=[],
                    material_texts=[]
                )
                OBJECTS.append(prev_obj)

            elif "SetDynamicObjectMaterialText".lower() in row.lower():
                alings = ["OBJECT_MATERIAL_TEXT_ALIGN_LEFT", "OBJECT_MATERIAL_TEXT_ALIGN_CENTER", "OBJECT_MATERIAL_TEXT_ALIGN_RIGHT"]
                size_strs: list[str] = ["OBJECT_MATERIAL_SIZE_32x32",
                                        "OBJECT_MATERIAL_SIZE_64x32",
                                        "OBJECT_MATERIAL_SIZE_64x64",
                                        "OBJECT_MATERIAL_SIZE_128x32",
                                        "OBJECT_MATERIAL_SIZE_128x64",
                                        "OBJECT_MATERIAL_SIZE_128x128",
                                        "OBJECT_MATERIAL_SIZE_256x32",
                                        "OBJECT_MATERIAL_SIZE_256x64",
                                        "OBJECT_MATERIAL_SIZE_256x128",
                                        "OBJECT_MATERIAL_SIZE_256x256",
                                        "OBJECT_MATERIAL_SIZE_512x64",
                                        "OBJECT_MATERIAL_SIZE_512x128",
                                        "OBJECT_MATERIAL_SIZE_512x256",
                                        "OBJECT_MATERIAL_SIZE_512x512"]

                textalignment: int = int(data[9] if data[9].strip().isdigit() else alings.index(data[9].strip()))
                size: int = int(data[3] if data[3].strip().isdigit() else 10 * (size_strs.index(data[3].strip()) + 1))

                mat_text = MaterialText(int(data[1]), 
                                        data[2].replace("\"", "").strip(),
                                        size, 
                                        data[4].replace("\"", "").strip(), 
                                        int(data[5]),
                                        bool(data[6]),
                                        int(data[7],0),
                                        int(data[8],0),
                                        textalignment)

                prev_obj.material_texts.append(mat_text)

            elif "SetDynamicObjectMaterial".lower() in row.lower():
                mat = Material(
                    material_index=int(data[1]),
                    model_id=int(data[2]),
                    txd_name=data[3].replace("\"", "").strip(),
                    texture_name=data[4].replace("\"", "").strip(),
                    material_color=data[5].replace("\"", "").strip()
                )
                prev_obj.materials.append(mat)

            if "RemoveBuildingForPlayer".lower() in row.lower():
                REMOVE_OBJECTS.append(RemoveObject(int(data[1].strip()), float(data[2].strip()), float(data[3].strip()), float(data[4].strip()), float(data[5].strip())))

        METADATA = Metadata(file_name, "", "", str(datetime.datetime.now()), [OBJECTS[0].x, OBJECTS[0].y, OBJECTS[0].z, OBJECTS[0].interior_id, OBJECTS[0].world_id], [], True)

        dump_map(file_name)


def dump_map(file_name: str):

    path = os.path.join("tools", "mapconverter", "dest", file_name)

    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, "metadata.json"), "w+") as jsonfile:
        jsonfile.write(json.dumps(METADATA, indent=4, default=lambda x: x.__dict__))

    with open(os.path.join(path, "objects.json"), "w+") as jsonfile:
        jsonfile.write(json.dumps(OBJECTS, indent=4, default=lambda x: x.__dict__))


    if len(REMOVE_OBJECTS) > 0:
        with open(os.path.join(path, "remove.json"), "w+") as jsonfile:
            jsonfile.write(json.dumps(REMOVE_OBJECTS, indent=4, default=lambda x: x.__dict__))


if __name__ == '__main__':
    APP()
