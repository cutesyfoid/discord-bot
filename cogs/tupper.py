# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

DB = "tupper.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tuppers (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id  INTEGER,
                user_id   INTEGER,
                name      TEXT,
                prefix    TEXT,
                avatar    TEXT
            )
        """)

class TupperGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="tupper", description="System postaci (TupperBox)")

    @app_commands.command(name="create", description="Stwórz nową postać")
    @app_commands.describe(
        nazwa="Nazwa postaci",
        prefiks="Prefiks który aktywuje postać (np. Ania:)",
        avatar="Zdjęcie avatara (opcjonalnie)"
    )
    async def create(self, interaction: discord.Interaction, nazwa: str, prefiks: str, avatar: discord.Attachment = None):
        avatar_url = avatar.url if avatar else None

        with get_db() as conn:
            existing = conn.execute(
                "SELECT id FROM tuppers WHERE guild_id=? AND user_id=? AND prefix=?",
                (interaction.guild_id, interaction.user.id, prefiks)
            ).fetchone()
            if existing:
                await interaction.response.send_message(
                    f"❌ Masz już postać z prefiksem `{prefiks}`!", ephemeral=True
                )
                return

            count = conn.execute(
                "SELECT COUNT(*) as c FROM tuppers WHERE guild_id=? AND user_id=?",
                (interaction.guild_id, interaction.user.id)
            ).fetchone()["c"]
            if count >= 10:
                await interaction.response.send_message(
                    "❌ Możesz mieć maksymalnie 10 postaci!", ephemeral=True
                )
                return

            conn.execute(
                "INSERT INTO tuppers (guild_id, user_id, name, prefix, avatar) VALUES (?,?,?,?,?)",
                (interaction.guild_id, interaction.user.id, nazwa, prefiks, avatar_url)
            )

        e = discord.Embed(title="✅ Postać stworzona!", color=0x2ecc71)
        e.add_field(name="Nazwa", value=nazwa)
        e.add_field(name="Prefiks", value=f"`{prefiks}`")
        if avatar_url:
            e.set_thumbnail(url=avatar_url)
        e.set_footer(text=f"Napisz '{prefiks} tekst' żeby użyć postaci")
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="list", description="Pokaż swoje postaci")
    async def list(self, interaction: discord.Interaction):
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM tuppers WHERE guild_id=? AND user_id=?",
                (interaction.guild_id, interaction.user.id)
            ).fetchall()

        if not rows:
            await interaction.response.send_message("Nie masz żadnych postaci!", ephemeral=True)
            return

        e = discord.Embed(title="🎭 Twoje postaci", color=0x9b59b6)
        for row in rows:
            avatar_info = "✅ Avatar ustawiony" if row["avatar"] else "❌ Brak avatara"
            e.add_field(
                name=f"{row['name']}",
                value=f"Prefiks: `{row['prefix']}`\n{avatar_info}",
                inline=True
            )
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="edit", description="Edytuj postać")
    @app_commands.describe(
        prefiks="Prefiks postaci którą chcesz edytować",
        nowa_nazwa="Nowa nazwa (opcjonalnie)",
        nowy_prefiks="Nowy prefiks (opcjonalnie)",
        nowy_avatar="Nowe zdjęcie avatara (opcjonalnie)"
    )
    async def edit(self, interaction: discord.Interaction, prefiks: str, nowa_nazwa: str = None, nowy_prefiks: str = None, nowy_avatar: discord.Attachment = None):
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM tuppers WHERE guild_id=? AND user_id=? AND prefix=?",
                (interaction.guild_id, interaction.user.id, prefiks)
            ).fetchone()

            if not row:
                await interaction.response.send_message(
                    f"❌ Nie masz postaci z prefiksem `{prefiks}`!", ephemeral=True
                )
                return

            new_name = nowa_nazwa or row["name"]
            new_prefix = nowy_prefiks or row["prefix"]
            new_avatar = nowy_avatar.url if nowy_avatar is not None else row["avatar"]

            conn.execute(
                "UPDATE tuppers SET name=?, prefix=?, avatar=? WHERE id=?",
                (new_name, new_prefix, new_avatar, row["id"])
            )

        e = discord.Embed(title="✅ Postać zaktualizowana!", color=0x2ecc71)
        e.add_field(name="Nazwa", value=new_name)
        e.add_field(name="Prefiks", value=f"`{new_prefix}`")
        if new_avatar:
            e.set_thumbnail(url=new_avatar)
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="delete", description="Usuń postać")
    @app_commands.describe(prefiks="Prefiks postaci którą chcesz usunąć")
    async def delete(self, interaction: discord.Interaction, prefiks: str):
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM tuppers WHERE guild_id=? AND user_id=? AND prefix=?",
                (interaction.guild_id, interaction.user.id, prefiks)
            ).fetchone()

            if not row:
                await interaction.response.send_message(
                    f"❌ Nie masz postaci z prefiksem `{prefiks}`!", ephemeral=True
                )
                return

            conn.execute("DELETE FROM tuppers WHERE id=?", (row["id"],))

        await interaction.response.send_message(
            f"✅ Postać **{row['name']}** została usunięta.", ephemeral=True
        )


class Tupper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        init_db()
        self.bot.tree.add_command(TupperGroup())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content
        if not content:
            return

        with get_db() as conn:
            tuppers = conn.execute(
                "SELECT * FROM tuppers WHERE guild_id=? AND user_id=?",
                (message.guild.id, message.author.id)
            ).fetchall()

        for tupper in tuppers:
            prefix = tupper["prefix"]
            if content.startswith(prefix):
                text = content[len(prefix):].strip()
                if not text:
                    return

                try:
                    webhooks = await message.channel.webhooks()
                    webhook = discord.utils.get(webhooks, name="TupperBot")
                    if not webhook:
                        webhook = await message.channel.create_webhook(name="TupperBot")
                except discord.Forbidden:
                    await message.channel.send(
                        "❌ Bot nie ma uprawnień do tworzenia webhooków!", delete_after=5
                    )
                    return

                try:
                    await message.delete()
                except discord.Forbidden:
                    pass

                avatar_url = tupper["avatar"] or message.author.display_avatar.url
                await webhook.send(
                    content=text,
                    username=tupper["name"],
                    avatar_url=avatar_url
                )
                break


async def setup(bot):
    await bot.add_cog(Tupper(bot))