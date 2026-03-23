# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import asyncio
import config

MEDIA_CHANNEL_IDS = [
    1483866197228523647,
    1483932486344900689,
]

MEDIA_EMOJIS = [
    "<a:serduszko:1484672343820341489>",
    "<a:slodkie:1484672376623857828>",
    "<a:serca:1484672407494197399>",
    "<a:kawaii:1484672441627447316>",
    "<a:sercebije:1484672934005178398>",
]

SZUKAJ_KOMENDY = {
    "!watek":   (1485412591772897340, "szuka wątku"),
    "!social":  (1485412615885815839, "szuka sociala"),
    "!relacje": (1485412643807297772, "szuka relacji"),
}

class Autoresponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.strip().lower()
        if content in SZUKAJ_KOMENDY:
            role_id, tekst = SZUKAJ_KOMENDY[content]
            role = message.guild.get_role(role_id)
            role_mention = role.mention if role else f"<@&{role_id}>"
            await message.channel.send(
                f"{message.author.mention} {tekst}! {role_mention}"
            )
            return

        if message.channel.id in MEDIA_CHANNEL_IDS and message.attachments:
            for emoji in MEDIA_EMOJIS:
                await message.add_reaction(emoji)
                await asyncio.sleep(0.5)
            return

        content_lower = message.content.lower()
        for trigger, response in config.AUTORESPONSES.items():
            if trigger.lower() in content_lower:
                await message.channel.send(response)
                break

async def setup(bot):
    await bot.add_cog(Autoresponder(bot))