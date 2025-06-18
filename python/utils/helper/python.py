import json
import random
import unicodedata
import time
import os
import uuid
import secrets
from typing import Any, Optional


def try_parse_int(value: str) -> Optional[int]:
	try:
		return int(value)
	except ValueError:
		return None


def try_parse_float(value: str) -> Optional[float]:
	try:
		return float(value)
	except ValueError:
		return None


def format_numbers(value: Any) -> str:
	if value is None:
		return ""
	return format(value, '3_d').replace(" ", "").replace("_", " ")


def timedelta_to_time(total_sec):
	h = total_sec // 3600
	m = (total_sec % 3600) // 60
	sec = (total_sec % 3600) % 60
	return int(h), int(m), int(sec)


def get_a_random_file(file_path: str) -> None | str:
	files = [file for file in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, file))]

	if not files:
		return None
	return os.path.join(file_path, random.choice(files))


def get_file(file_path: str, file_name: str) -> str:
	with open(os.path.join(file_path, file_name), "r") as f:
		return f.read()


def get_files_data(file_path: str, ignore_char: str = "_") -> list[str]:
	result = []
	files = [file for file in os.listdir(file_path) if
	         os.path.isfile(os.path.join(file_path, file)) and not file.startswith(ignore_char)]

	for file in files:
		with open(os.path.join(file_path, file), "r") as f:
			result.append(f.read())
	return result


def load_all_files(file_path: str) -> None | list[str]:
	files = [file for file in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, file))]
	ret = []

	for file in files:
		with open(os.path.join(file_path, file), "r") as f:
			ret.append(json.load(f))

	return ret


def load_json_file(file_path: str) -> Any:
	with open(os.path.join(file_path), "r") as f:
		return json.load(f)


def round_to_nearest_hundred(number):
	return round(number / 100) * 100


def round_to_nearest(number, n: int):
	return round(number / n) * n


def fixchars(string: str):
	return "".join([getfixchar(i) for i in string])


def getfixchar(char: str):
	match char:
		case "ö":
			return "¨"
		case "Ö":
			return "‘"
		case "ü":
			return "¬"
		case 'Ü':
			return '•'
		case 'ó':
			return '¦'
		case 'Ó':
			return 'Ź'
		case 'ő':
			return '§'
		case 'Ő':
			return '§'
		case 'ú':
			return 'Ş'
		case 'Ú':
			return '“'
		case 'é':
			return 'ž'
		case 'É':
			return '‡'
		case 'á':
			return 'a'
		case 'Á':
			return 'A'
		case 'ű':
			return '«'
		case 'Ű':
			return '·'
		case 'í':
			return '˘'
		case 'Í':
			return '‹'
		case _:
			return char


def clen_text(text: str) -> str:
	normalized_text = unicodedata.normalize('NFKD', text)
	ascii_text = ''.join(c for c in normalized_text if ord(c) < 128)
	return ascii_text


def get_uuid7():
	nanoseconds = time.time_ns()
	unix_ts_ms = nanoseconds // 1_000_000
	ts_part = unix_ts_ms & 0xFFFFFFFFFFFF

	random_bytes = secrets.token_bytes(10)
	rand_a = int.from_bytes(random_bytes[0:2], 'big') & 0x0FFF
	rand_b = int.from_bytes(random_bytes[2:10], 'big') & 0x3FFFFFFFFFFFFFFF

	version = 0x7
	variant = 0x2

	uuid_int = ts_part << (128 - 48)
	uuid_int |= version << (128 - 48 - 4)  # Shift left by 76 bits
	uuid_int |= rand_a << (128 - 48 - 4 - 12)  # Shift left by 64 bits
	uuid_int |= variant << (128 - 48 - 4 - 12 - 2)  # Shift left by 62 bits
	uuid_int |= rand_b

	return uuid.UUID(int=uuid_int)

