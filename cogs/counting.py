import discord
from discord.ext import commands
import json
import os
import config

COUNT_FILE = "counting.json"

CORRECT_EMOJI = "<a:1477805833260634182:1485375937561362482>"
WRONG_EMOJI = "<:936060insanelaughingemoji:1485375808422805514>"

def load():
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE) as f:
            return json.load(f)
    return {"count": 0}

def save(data):
    with open(COUNT_FILE, "w") as f:
        json.dump(data, f)

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.id != config.COUNTING_CHANNEL_ID:
            return

        try:
            number = int(message.content.strip())
        except ValueError:
            await message.delete()
            return

        expected = self.data["count"] + 1

        if number == expected:
            self.data["count"] = number
            save(self.data)
            await message.add_reaction(CORRECT_EMOJI)

            if number % 100 == 0:
                await message.channel.send(f"Osiagnelismy **{number}**! Super robota!")
        else:
            await message.add_reaction(WRONG_EMOJI)
            await message.channel.send(
                f"{message.author.mention} pomylil sie! Nastepna liczba to **{expected}**, ale odliczanie resetuje sie do **0**!",
                delete_after=5
            )
            self.data = {"count": 0}
            save(self.data)

async def setup(bot):
    await bot.add_cog(Counting(bot))