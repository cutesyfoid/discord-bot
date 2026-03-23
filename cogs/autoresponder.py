import discord
from discord.ext import commands
import config

MEDIA_CHANNEL_ID = 1485382435880570962

MEDIA_EMOJIS = [
    "<:964657bunny:1485375844695412940>",
    "<:57086star:1485375872155258890>",
    "<:936060insanelaughingemoji:1485375808422805514>",
    "<a:1477805833260634182:1485375937561362482>",
]

SZUKAJ_KOMENDY = {
    "!watek":   (1485412591772897340, "szuka watku"),
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

        # komendy szukaj
        content = message.content.strip().lower()
        if content in SZUKAJ_KOMENDY:
            role_id, tekst = SZUKAJ_KOMENDY[content]
            role = message.guild.get_role(role_id)
            role_mention = role.mention if role else f"<@&{role_id}>"
            await message.channel.send(
                f"{message.author.mention} {tekst}! {role_mention}"
            )
            return

        # reakcje na pliki w kanale media
        if message.channel.id == MEDIA_CHANNEL_ID and message.attachments:
            for emoji in MEDIA_EMOJIS:
                await message.add_reaction(emoji)
            return

        # autoresponder
        content_lower = message.content.lower()
        for trigger, response in config.AUTORESPONSES.items():
            if trigger.lower() in content_lower:
                await message.channel.send(response)
                break

async def setup(bot):
    await bot.add_cog(Autoresponder(bot))