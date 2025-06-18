import os
import tomllib

def main():
    all_keys: list[str] = []

    for root, _, files in os.walk("configs/languages"):
        for file in files:
            with open(os.path.join(root, file), "rb") as f:
                translation_keys = [x.lower() for x in tomllib.load(f)["translations"].keys()]
                all_keys.extend(translation_keys)

    distinct_keys: list[str] = sorted(set(all_keys))

    with open(os.path.join("python/utils/enums", "translation_keys.py"), "w+") as f:
        f.write("""from enum import StrEnum
    
    
class TranslationKeys(StrEnum):
""")

        for key in distinct_keys:
            f.write(f'    {key.upper()} = "{key.lower()}"\n')


if __name__ == '__main__':
    main()