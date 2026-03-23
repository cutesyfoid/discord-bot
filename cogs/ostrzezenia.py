# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from contextlib import contextmanager

DB = "warnings.db"
WARN_CHANNEL_ID = 1483866196490326061
MAX_WARNINGS = 3

@contextmanager
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id  INTEGER,
                user_id   INTEGER,
                mod_id    INTEGER,
                reason    TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

class Ostrzezenia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        init_db()

    @app_commands.command(name="warn", description="Ostrzeż użytkownika")
    @app_commands.describe(member="Użytkownik", reason="Powód ostrzeżenia")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Brak powodu"):
        if member.bot:
            await interaction.response.send_message("Nie możesz ostrzegać botów!", ephemeral=True)
            return
        if member == interaction.user:
            await interaction.response.send_message("Nie możesz ostrzegać siebie!", ephemeral=True)
            return

        with get_db() as conn:
            conn.execute(
                "INSERT INTO warnings (guild_id, user_id, mod_id, reason) VALUES (?,?,?,?)",
                (interaction.guild_id, member.id, interaction.user.id, reason)
            )
            count = conn.execute(
                "SELECT COUNT(*) as c FROM warnings WHERE guild_id=? AND user_id=?",
                (interaction.guild_id, member.id)
            ).fetchone()["c"]

        warn_channel = interaction.guild.get_channel(WARN_CHANNEL_ID)
        e = discord.Embed(title="⚠️ Ostrzeżenie", color=0xf39c12)
        e.add_field(name="Użytkownik", value=f"{member.mention} (`{member.id}`)")
        e.add_field(name="Moderator", value=interaction.user.mention)
        e.add_field(name="Powód", value=reason, inline=False)
        e.add_field(name="Liczba ostrzeżeń", value=f"**{count}** / {MAX_WARNINGS}")
        e.set_thumbnail(url=member.display_avatar.url)
        e.timestamp = discord.utils.utcnow()

        if warn_channel:
            await warn_channel.send(embed=e)

        try:
            dm_embed = discord.Embed(
                title="⚠️ Otrzymałeś ostrzeżenie",
                description=f"Otrzymałeś ostrzeżenie na serwerze **{interaction.guild.name}**.",
                color=0xf39c12
            )
            dm_embed.add_field(name="Powód", value=reason, inline=False)
            dm_embed.add_field(name="Liczba ostrzeżeń", value=f"**{count}** / {MAX_WARNINGS}")
            if count >= MAX_WARNINGS:
                dm_embed.add_field(name="⚠️ Uwaga", value="Osiągnąłeś maksymalną liczbę ostrzeżeń i zostałeś wyrzucony z serwera.", inline=False)
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Ostrzeżono",
                description=f"{member.mention} otrzymał ostrzeżenie nr **{count}**.\nPowód: {reason}",
                color=0xf39c12
            )
        )

        if count >= MAX_WARNINGS:
            try:
                await member.kick(reason=f"Automatyczny kick po {MAX_WARNINGS} ostrzeżeniach.")
                if warn_channel:
                    await warn_channel.send(embed=discord.Embed(
                        title="👢 Auto-kick",
                        description=f"{member.mention} został wyrzucony po osiągnięciu **{MAX_WARNINGS}** ostrzeżeń.",
                        color=0xe74c3c
                    ))
            except discord.Forbidden:
                pass

    @app_commands.command(name="warnings", description="Sprawdź ostrzeżenia użytkownika")
    @app_commands.describe(member="Użytkownik")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM warnings WHERE guild_id=? AND user_id=? ORDER BY timestamp DESC",
                (interaction.guild_id, member.id)
            ).fetchall()

        if not rows:
            await interaction.response.send_message(f"{member.mention} nie ma żadnych ostrzeżeń.", ephemeral=True)
            return

        e = discord.Embed(title=f"⚠️ Ostrzeżenia — {member.display_name}", color=0xf39c12)
        e.set_thumbnail(url=member.display_avatar.url)
        for row in rows:
            mod = interaction.guild.get_member(row["mod_id"])
            mod_name = mod.mention if mod else f"`{row['mod_id']}`"
            e.add_field(
                name=f"#{row['id']} — {row['timestamp']}",
                value=f"**Powód:** {row['reason']}\n**Moderator:** {mod_name}",
                inline=False
            )
        e.set_footer(text=f"Łącznie: {len(rows)} / {MAX_WARNINGS}")
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="delwarn", description="Usuń ostrzeżenie użytkownika po ID")
    @app_commands.describe(member="Użytkownik", warn_id="ID ostrzeżenia")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def delwarn(self, interaction: discord.Interaction, member: discord.Member, warn_id: int):
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM warnings WHERE id=? AND guild_id=? AND user_id=?",
                (warn_id, interaction.guild_id, member.id)
            ).fetchone()

            if not row:
                await interaction.response.send_message(
                    f"Nie znaleziono ostrzeżenia #{warn_id} dla {member.mention}.", ephemeral=True
                )
                return

            conn.execute("DELETE FROM warnings WHERE id=?", (warn_id,))

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Usunięto ostrzeżenie",
                description=f"Ostrzeżenie **#{warn_id}** użytkownika {member.mention} zostało usunięte.",
                color=0x2ecc71
            )
        )

    @warn.error
    @warnings.error
    @delwarn.error
    async def error_handler(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(
            embed=discord.Embed(title="❌ Błąd", description="Brak uprawnień lub inny błąd.", color=0xe74c3c),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Ostrzezenia(bot))