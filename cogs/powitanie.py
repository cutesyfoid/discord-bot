import discord
from discord.ext import commands
import config

class Powitanie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(config.WELCOME_CHANNEL_ID)
        if not channel:
            return

        await channel.send(
            f"siema {member.mention}, witaj na serwerze!",
            file=discord.File("welcome.jpg")
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.get_channel(config.WELCOME_CHANNEL_ID)
        if not channel:
            return

        await channel.send(f"**{member}** opuścił serwer. nara!")

async def setup(bot):
    await bot.add_cog(Powitanie(bot))