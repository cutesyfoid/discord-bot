import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import time
import math
import config

DB = "leveling.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS levels (
                guild_id INTEGER,
                user_id  INTEGER,
                xp       INTEGER DEFAULT 0,
                level    INTEGER DEFAULT 0,
                last_xp  INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        """)

def xp_for_level(lvl: int) -> int:
    """XP potrzebne do osiągnięcia poziomu lvl"""
    return math.floor(100 * (lvl ** 1.5))

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        init_db()

    def get_user(self, guild_id, user_id):
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM levels WHERE guild_id=? AND user_id=?",
                (guild_id, user_id)
            ).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO levels (guild_id, user_id) VALUES (?,?)",
                    (guild_id, user_id)
                )
                return {"xp": 0, "level": 0, "last_xp": 0}
            return dict(row)

    def add_xp(self, guild_id, user_id, amount):
        user = self.get_user(guild_id, user_id)
        new_xp = user["xp"] + amount
        new_level = user["level"]

        leveled_up = False
        while new_xp >= xp_for_level(new_level + 1):
            new_level += 1
            leveled_up = True

        with get_db() as conn:
            conn.execute(
                "UPDATE levels SET xp=?, level=?, last_xp=? WHERE guild_id=? AND user_id=?",
                (new_xp, new_level, int(time.time()), guild_id, user_id)
            )
        return leveled_up, new_level

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        user = self.get_user(message.guild.id, message.author.id)
        now = int(time.time())

        if now - user["last_xp"] < config.XP_COOLDOWN_SECONDS:
            return

        leveled_up, new_level = self.add_xp(
            message.guild.id, message.author.id, config.XP_PER_MESSAGE
        )

        if leveled_up:
            channel = (
                message.guild.get_channel(config.LEVEL_UP_CHANNEL_ID)
                if config.LEVEL_UP_CHANNEL_ID else message.channel
            )
            e = discord.Embed(
                title="🎉 Level Up!",
                description=f"{message.author.mention} osiągnął poziom **{new_level}**! 🚀",
                color=0xf1c40f
            )
            e.set_thumbnail(url=message.author.display_avatar.url)
            await channel.send(embed=e)

    @app_commands.command(name="rank", description="Sprawdź swój rank lub innego gracza")
    @app_commands.describe(member="Użytkownik (opcjonalnie)")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = self.get_user(interaction.guild_id, member.id)
        lvl = user["level"]
        xp = user["xp"]
        needed = xp_for_level(lvl + 1)

        bar_len = 20
        filled = int(bar_len * xp / needed) if needed else bar_len
        bar = "█" * filled + "░" * (bar_len - filled)

        e = discord.Embed(title=f"📊 Rank — {member.display_name}", color=0x3498db)
        e.add_field(name="Poziom", value=f"**{lvl}**", inline=True)
        e.add_field(name="XP", value=f"**{xp}** / {needed}", inline=True)
        e.add_field(name="Postęp", value=f"`{bar}`", inline=False)
        e.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="leaderboard", description="Top 10 graczy na serwerze")
    async def leaderboard(self, interaction: discord.Interaction):
        with get_db() as conn:
            rows = conn.execute(
                "SELECT user_id, xp, level FROM levels WHERE guild_id=? ORDER BY xp DESC LIMIT 10",
                (interaction.guild_id,)
            ).fetchall()

        if not rows:
            await interaction.response.send_message("Brak danych!", ephemeral=True)
            return

        medals = ["🥇", "🥈", "🥉"]
        desc = ""
        for i, row in enumerate(rows):
            medal = medals[i] if i < 3 else f"`#{i+1}`"
            user = interaction.guild.get_member(row["user_id"])
            name = user.display_name if user else f"<@{row['user_id']}>"
            desc += f"{medal} **{name}** — Lvl {row['level']} ({row['xp']} XP)\n"

        e = discord.Embed(title="🏆 Leaderboard", description=desc, color=0xf1c40f)
        await interaction.response.send_message(embed=e)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
