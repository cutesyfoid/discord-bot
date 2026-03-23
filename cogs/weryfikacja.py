import discord
from discord.ext import commands
from discord import app_commands
import config

class WeryfikacjaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistent

    @discord.ui.button(label="✅ Zweryfikuj się", style=discord.ButtonStyle.success, custom_id="verify_btn")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config.VERIFIED_ROLE_ID)
        if not role:
            await interaction.response.send_message("❌ Rola weryfikacji nie istnieje. Skontaktuj się z adminem.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("✅ Jesteś już zweryfikowany!", ephemeral=True)
            return

        await interaction.user.add_roles(role)
        await interaction.response.send_message("🎉 Zweryfikowano! Witaj na serwerze!", ephemeral=True)

class Weryfikacja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(WeryfikacjaView())  # persistent view po restarcie

    @app_commands.command(name="weryfikacja_setup", description="Wyślij embed z przyciskiem weryfikacji")
    @app_commands.checks.has_permissions(administrator=True)
    async def weryfikacja_setup(self, interaction: discord.Interaction):
        e = discord.Embed(
            title="✅ Weryfikacja",
            description=(
                "Aby uzyskać dostęp do serwera, kliknij przycisk poniżej.\n\n"
                "Klikając, akceptujesz regulamin serwera. 📜"
            ),
            color=0x2ecc71
        )
        channel = interaction.guild.get_channel(config.VERIFY_CHANNEL_ID) or interaction.channel
        await channel.send(embed=e, view=WeryfikacjaView())
        await interaction.response.send_message("✅ Panel weryfikacji wysłany!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Weryfikacja(bot))
