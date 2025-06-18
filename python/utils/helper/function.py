import hashlib
import os

from samp import CallRemoteFunction  # type: ignore

from typing import List, Optional
from python.model.database import Skin as SkinDB
from python.database.context_managger import transactional_session
from python.server.database import BUSINESS_SESSION


def get_weapon_slot_name(slot: int) -> str:
    match slot:
        case 1:
            return "Kényszerítő eszköz"

        case 2:
            return "Marok lőfegyver"

        case 9:
            return "Kiegészítő eszköz"
    return "N/A"


def get_weapon_max_ammo(weapon_id: int, magazine: int = 1) -> int:
    match weapon_id:
        case 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15:
            return 1 * magazine

        case 16 | 17 | 18:
            return 2 * magazine

        case 22 | 23:
            return 17 * magazine

        case 24:
            return 7 * magazine

        case 25 | 27:
            return 7 * magazine

        case 26:
            return 3 * magazine

        case 28:
            return 25 * magazine

        case 29 | 30:
            return 30 * magazine

        case 31 | 32:
            return 50 * magazine

        case 33:
            return 5 * magazine

        case 34:
            return 5 * magazine

        case 41:
            return 200 * magazine

        case 43:
            return 30 * magazine

        case 0:
            return 0 * magazine

        case _:
            return 1 * magazine


def get_skin_id(skin_id: int):
    with transactional_session(BUSINESS_SESSION) as session:
        skin: SkinDB = session.query(SkinDB).filter(SkinDB.id == skin_id).one()
        return skin.gta_id


def get_weapon_name(weapon_id: int) -> str:
    match weapon_id:
        case 0: return "Ököl"
        case 1: return "Boxer"
        case 2: return "Golf üto"
        case 3: return "Gumibot"
        case 4: return "Kés"
        case 5: return "Baseball üto"
        case 6: return "Lapát"
        case 7: return "Biliárd dákó"
        case 8: return "Katana"
        case 9: return "Láncfurűsz"
        case 10: return "Rózsaszín Dildó"
        case 11: return "Nagy Fehér Vibrátor"
        case 12: return "Közepes Fehér Vibrátor"
        case 13: return "Kis Fehér Vibrátor"
        case 14: return "Virág"
        case 15: return "Bot"
        case 16: return "Gránát"
        case 17: return "Könnygáz"
        case 18: return "Molotov-koktél"
        case 22: return "Colt45"
        case 23: return "Módosított Colt45"
        case 24: return "Desert Eagle"
        case 25: return "Mossberg 590A1"
        case 26: return "B MP-43"
        case 27: return "SPAZ-12"
        case 28: return "MAC-10"
        case 29: return "HK MP5"
        case 30: return "AK-47"
        case 31: return "M4"
        case 32: return "TEC-9"
        case 33: return "Winchester M92"
        case 34: return "HK PSG1"
        case 35: return "RPG-7"
        case 36: return "Hokőveto-rakéta"
        case 37: return "Lángszóró"
        case 38: return "Minigun"
        case 39: return "Satchel"
        case 40: return "Detonátor"
        case 41: return "Spray"
        case 42: return "Tuzoltó készülék"
        case 43: return "Fénykőpezogép"
        case 44: return "Éjjellűtó"
        case 45: return "Hőkamera"
        case 46: return "Ejtoernyo"
        case 49: return "Autó"
        case 50: return "Helikopter"
        case 51: return "Robbanás"
        case 53: return "Fulladás"
        case 54: return "Zuhanás"
        case 255: return "Öngyilkosság"
        case _:
            return "Unknown Weapon ID"


def get_slot_weapons(slot: int) -> List[int]:
    match slot:
        case 0: return [0, 1]
        case 1:  return [2, 3, 4, 5, 6, 7, 8, 9]
        case 2:  return [22, 23, 24]
        case 3:  return [25, 26, 27]
        case 4:  return [28, 29, 32]
        case 5:  return [30, 31]
        case 6:  return [33, 34]
        case 7:  return [35, 36, 37, 38]
        case 8:  return [16, 17, 18, 39]
        case 9:  return [41, 42, 43]
        case 10: return  [10, 11, 12, 13, 14, 15]
        case 11: return  [44, 45, 46]
        case 12: return  [40]
        case _:
            return []


def get_weapon_slot(weapon_id: int) -> Optional[int]:
    match weapon_id:
        case 0 | 1:
            return 0
        case 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
            return 1
        case 22 | 23 | 24:
            return 2
        case 25 | 26 | 27:
            return 3
        case 28 | 29 | 32:
            return 4
        case 30 | 31:
            return 5
        case 33 | 34:
            return 6
        case 35 | 36 | 37 | 38:
            return 7
        case 16 | 17 | 18 | 39:
            return 8
        case 41 | 42 | 43:
            return 9
        case 10 | 11 | 12 | 13 | 14 | 15:
            return 10
        case 44 | 45 | 46:
            return 11
        case 40:
            return 12
        case _:
            return None


def get_md5_dir_hash(directory: str) -> str:
    """
    Calculates an MD5 hash representing the content of all files
    within a directory and its subdirectories.

    Args:
        directory: The path to the directory.

    Returns:
        The hexadecimal MD5 hash string.
        Returns "-1" if the directory doesn't exist.
        Returns "-2" if a major error occurs during traversal.
        Individual file read errors are printed but skipped.
    """
    md5_hash = hashlib.md5()

    if not os.path.isdir(directory): # More specific check than os.path.exists
        return "-1" # Indicates directory not found or is not a directory

    try:
        # For deterministic hashing, sort directories and files
        for root, dirs, files in os.walk(directory):
            # Sort directory names to ensure consistent traversal order
            dirs.sort()
            # Sort file names to ensure consistent processing order
            files.sort()

            for name in files:
                filepath = os.path.join(root, name)
                try:
                    # Process only regular files (skip symlinks, etc. if needed)
                    if os.path.isfile(filepath):
                        with open(filepath, 'rb') as f_obj:
                            # Read and update hash string content in blocks
                            while True:
                                buf = f_obj.read(4096)
                                if not buf:
                                    break
                                md5_hash.update(buf)
                except (IOError, OSError) as e:
                    # Log or handle error for specific file (e.g., permission denied)
                    print(f"Warning: Could not read file {filepath}: {e}")
                    # Continue hashing other files
                    continue
                except Exception as e:
                    # Handle unexpected errors during file processing
                    print(f"Error processing file {filepath}: {e}")
                    # Depending on requirements, you might want to re-raise or return an error code
                    return "-3" # Or some other indicator for file processing error

    except Exception as e:
        print(f"Error walking directory {directory}: {e}")
        return "-2" # Indicates a traversal error

    return md5_hash.hexdigest()


def wrap_color(color: str, txt: str) -> str:
    return "{" + color + "}" + txt + "{FFFFFF}"


def get_z_coord_from_x_y(x: float, y: float) -> float:
    return float(f"{CallRemoteFunction("PyFindZUpper", x, y)}.{CallRemoteFunction("PyFindZDown", x, y)}")
