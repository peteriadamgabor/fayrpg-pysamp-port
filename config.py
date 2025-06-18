
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    secrets=["configs/.secrets.toml"],
    settings_files=['.env', 
                    'configs/anti_cheat.settings.toml',
                    'configs/database.settings.toml',
                    'configs/paths.settings.toml',
                    'configs/server.settings.toml',
                    'configs/email.settings.toml',
                    ],
    load_dotenv=True,
)