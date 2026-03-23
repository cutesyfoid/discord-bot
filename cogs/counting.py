# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import json
import os
import config

COUNT_FILE = "counting.json"

CORRECT_EMOJI = "<a:checkmark:1484522545519525949>"
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
            return

        expected = self.data["count"] + 1

        if number == expected:
            self.data["count"] = number
            save(self.data)
            await message.add_reaction(CORRECT_EMOJI)
        else:
            await message.add_reaction(WRONG_EMOJI)
            await message.channel.send(
                f"<:sideeye:1484559896920850442> {message.author.mention}, zgubiłeś rytm. W tym mieście nie ma miejsca na pomyłki. Odliczanie zostało zresetowane.",
                delete_after=10
            )
            self.data = {"count": 0}
            save(self.data)

async def setup(bot):
    await bot.add_cog(Counting(bot))