# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
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
    "cogs.tupper",
    "cogs.ostrzezenia",
    "cogs.muzeum",
]

GUILD_ID = 1483866194804084768

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

        # Instant sync on your main/test guild
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        log.info("Slash commands zsynchronizowane (guild)")

        # Global sync — works on all servers (up to 1 hour to propagate)
        await self.tree.sync()
        log.info("Slash commands zsynchronizowane globalnie")

    async def on_ready(self):
        log.info(f"Bot uruchomiony jako {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="welcome\u2003to\u2003new\u2003york\u2003city."
            )
        )

bot = MyBot()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        log.critical("Brak DISCORD_TOKEN w pliku .env!")
        exit(1)
    bot.run(token)
