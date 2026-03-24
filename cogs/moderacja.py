# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import config
from datetime import timedelta

class Moderacja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def embed(self, title, desc, color):
        return discord.Embed(title=title, description=desc, color=color)

    @app_commands.command(name="kick", description="Wyrzuca użytkownika z serwera")
    @app_commands.describe(member="Użytkownik", reason="Powód")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Brak powodu"):
        await member.kick(reason=reason)
        await interaction.response.send_message(
            embed=self.embed("👢 Kick", f"**{member}** został wyrzucony.\n📝 Powód: {reason}", config.COLOR_WARN)
        )

    @app_commands.command(name="ban", description="Banuje użytkownika")
    @app_commands.describe(member="Użytkownik", reason="Powód")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Brak powodu"):
        await member.ban(reason=reason)
        await interaction.response.send_message(
            embed=self.embed("🔨 Ban", f"**{member}** został zbanowany.\n📝 Powód: {reason}", config.COLOR_ERR)
        )

    @app_commands.command(name="unban", description="Odbanowuje użytkownika po ID")
    @app_commands.describe(user_id="ID użytkownika")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        user = await self.bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(
            embed=self.embed("✅ Unban", f"**{user}** został odbanowany.", config.COLOR_OK)
        )

    @app_commands.command(name="mute", description="Wycisza użytkownika (timeout)")
    @app_commands.describe(member="Użytkownik", minuty="Czas w minutach", reason="Powód")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minuty: int = 10, reason: str = "Brak powodu"):
        await member.timeout(timedelta(minutes=minuty), reason=reason)
        await interaction.response.send_message(
            embed=self.embed("🔇 Mute", f"**{member}** wyciszony na **{minuty} min**.\n📝 Powód: {reason}", config.COLOR_WARN)
        )

    @app_commands.command(name="unmute", description="Zdejmuje timeout z użytkownika")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(
            embed=self.embed("🔊 Unmute", f"**{member}** został odciszony.", config.COLOR_OK)
        )

    @app_commands.command(name="clear", description="Usuwa wiadomości z kanału")
    @app_commands.describe(ilosc="Liczba wiadomości (max 67)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, ilosc: int = 10):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=min(ilosc, 100))
        await interaction.followup.send(
            embed=self.embed("🧹 Clear", f"Usunięto **{len(deleted)}** wiadomości.", config.COLOR_OK),
            ephemeral=True
        )

    @kick.error
    @ban.error
    @mute.error
    @clear.error
    async def perm_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(
            embed=self.embed("❌ Błąd", "Brak uprawnień lub inny błąd.", config.COLOR_ERR),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Moderacja(bot))