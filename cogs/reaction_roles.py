# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import config

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.add_reactions()

    async def add_reactions(self):
        for guild in self.bot.guilds:
            # reakcja weryfikacji
            try:
                ch = guild.get_channel(config.VERIFY_CHANNEL_ID)
                msg = await ch.fetch_message(config.VERIFY_MESSAGE_ID)
                await msg.add_reaction(config.VERIFY_EMOJI)
            except Exception:
                pass

            # reakcje autorole
            for msg_id, emojis in config.REACTION_ROLES.items():
                try:
                    ch = guild.get_channel(config.AUTOROLE_CHANNEL_ID)
                    msg = await ch.fetch_message(msg_id)
                    for emoji in emojis.keys():
                        await msg.add_reaction(emoji)
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = str(payload.emoji)

        # weryfikacja
        if payload.message_id == config.VERIFY_MESSAGE_ID:
            if emoji == config.VERIFY_EMOJI:
                role = guild.get_role(config.VERIFIED_ROLE_ID)
                if role and member:
                    await member.add_roles(role)
            return

        # autorole
        if payload.message_id in config.REACTION_ROLES:
            role_id = config.REACTION_ROLES[payload.message_id].get(emoji)
            if role_id:
                role = guild.get_role(role_id)
                if role and member:
                    await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id == config.VERIFY_MESSAGE_ID:
            return

        if payload.message_id in config.REACTION_ROLES:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            emoji = str(payload.emoji)
            role_id = config.REACTION_ROLES[payload.message_id].get(emoji)
            if role_id:
                role = guild.get_role(role_id)
                if role and member:
                    await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))