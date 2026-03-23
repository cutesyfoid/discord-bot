# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import config

class Logi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log(self, guild, embed):
        channel = guild.get_channel(config.LOG_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        e = discord.Embed(title="🗑️ Usunięta wiadomość", color=0xe74c3c)
        e.add_field(name="Autor", value=message.author.mention)
        e.add_field(name="Kanał", value=message.channel.mention)
        e.add_field(name="Treść", value=message.content[:1024] or "*brak tekstu*", inline=False)
        e.timestamp = discord.utils.utcnow()
        await self.log(message.guild, e)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        e = discord.Embed(title="✏️ Edytowana wiadomość", color=0xf39c12)
        e.add_field(name="Autor", value=before.author.mention)
        e.add_field(name="Kanał", value=before.channel.mention)
        e.add_field(name="Przed", value=before.content[:512] or "*brak*", inline=False)
        e.add_field(name="Po", value=after.content[:512] or "*brak*", inline=False)
        e.timestamp = discord.utils.utcnow()
        await self.log(before.guild, e)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        e = discord.Embed(title="✅ Nowy użytkownik", color=0x2ecc71)
        e.add_field(name="Użytkownik", value=f"{member} ({member.id})")
        e.add_field(name="Konto założone", value=discord.utils.format_dt(member.created_at, 'R'))
        e.set_thumbnail(url=member.display_avatar.url)
        e.timestamp = discord.utils.utcnow()
        await self.log(member.guild, e)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        e = discord.Embed(title="❌ Użytkownik opuścił serwer", color=0xe74c3c)
        e.add_field(name="Użytkownik", value=f"{member} ({member.id})")
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        e.add_field(name="Role", value=", ".join(roles) or "Brak", inline=False)
        e.set_thumbnail(url=member.display_avatar.url)
        e.timestamp = discord.utils.utcnow()
        await self.log(member.guild, e)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        added = set(after.roles) - set(before.roles)
        removed = set(before.roles) - set(after.roles)
        if not added and not removed:
            return
        e = discord.Embed(title="🔄 Zmiana roli", color=0x3498db)
        e.add_field(name="Użytkownik", value=after.mention)
        if added:
            e.add_field(name="➕ Dodano", value=", ".join(r.mention for r in added))
        if removed:
            e.add_field(name="➖ Usunięto", value=", ".join(r.mention for r in removed))
        e.timestamp = discord.utils.utcnow()
        await self.log(after.guild, e)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        e = discord.Embed(title="🔨 Ban", description=f"{user} ({user.id}) został zbanowany.", color=0xe74c3c)
        e.timestamp = discord.utils.utcnow()
        await self.log(guild, e)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        e = discord.Embed(title="✅ Unban", description=f"{user} ({user.id}) został odbanowany.", color=0x2ecc71)
        e.timestamp = discord.utils.utcnow()
        await self.log(guild, e)

async def setup(bot):
    await bot.add_cog(Logi(bot))