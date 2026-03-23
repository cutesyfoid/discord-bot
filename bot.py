import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import subprocess
subprocess.run(["pip", "install", "-U", "yt-dlp"], capture_output=True)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("bot")

COGS = [
    "cogs.moderacja",
    "cogs.powitanie",
    "cogs.leveling",
    "cogs.logi",
    "cogs.autoresponder",
    "cogs.reaction_roles",
    "cogs.weryfikacja",
    "cogs.counting",
    "cogs.muzyka",
]

GUILD_ID = 1485366823762530357

intents = discord.Intents.all()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(cog)
                log.info(f"Zaladowano: {cog}")
            except Exception as e:
                log.error(f"Blad ladowania {cog}: {e}")

        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        log.info("Slash commands zsynchronizowane")

    async def on_ready(self):
        log.info(f"Bot uruchomiony jako {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="serwer"
            )
        )

bot = MyBot()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        log.critical("Brak DISCORD_TOKEN w pliku .env!")
        exit(1)
    bot.run(token)