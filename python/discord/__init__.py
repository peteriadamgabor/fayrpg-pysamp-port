import atexit
from config import settings
from discord_webhook import DiscordWebhook, DiscordEmbed


def init_module():
    print(f"Module {__name__} is being initialized.")

    discord_webhook: DiscordWebhook = DiscordWebhook(url=settings.server.discord_hooks["main"])

    embed = DiscordEmbed(title="Discord hook test", description="Discord hook modul loaded ✅", color="ff8080")

    discord_webhook.add_embed(embed)
    discord_webhook.execute()


def unload_module():
    print(f"Module {__name__} is being unloaded.")

    discord_webhook: DiscordWebhook = DiscordWebhook(url=settings.server.discord_hooks["main"])

    embed = DiscordEmbed(title="Discord hook test", description="Discord hook modul unloaded ❌", color="ff8080")

    discord_webhook.add_embed(embed)
    discord_webhook.execute()


atexit.register(unload_module)

init_module()


def send_embed(title: str, description: str, color: str, hook: str = "main"):
    discord_webhook: DiscordWebhook = DiscordWebhook(url=settings.server.discord_hooks[hook])

    discord_webhook.add_embed(DiscordEmbed(title=title, description=description, color=color))
    discord_webhook.execute()