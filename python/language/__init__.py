import os
import tomllib
from config import settings

TRANSLATIONS: dict[str, dict[str, str]] = {}


def load_translations():
    global TRANSLATIONS

    temp_dict: dict[str, dict[str, str]] = {}

    for root, _, files in os.walk(settings.paths.LANGUAGES):
        for file in [fl for fl in files if fl.endswith(".toml") and not fl.endswith("_.toml")]:
            with open(os.path.join(root, file), "rb") as f:
                toml_content = tomllib.load(f)

                lang: str | None = toml_content.get("set1", None)
                translations: dict[str, str] | None = toml_content.get("translations", None)

                if lang is None or translations is None:
                    continue

                if  lang in temp_dict:
                    temp_dict[lang].update(translations)

                else:
                    temp_dict.setdefault(lang.lower(), translations)

    TRANSLATIONS = {key.lower(): { ikey.lower(): ivalue for ikey, ivalue in value.items() } for key, value in temp_dict.items()}

def get_translated_text(str_key: str, language: str = "hu", *args):
    if lang_texts := TRANSLATIONS.get(language, None):
        if text := lang_texts.get(str_key.lower(), None):
            return text.format(*args)

    return str_key

load_translations()
