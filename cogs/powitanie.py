# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from datetime import timedelta

WELCOME_CHANNEL_ID = 1483866196490326058

AUTO_ROLE_IDS = [
    1483866194804084770,
    1483866194804084773,
    1483866195261395157,
    1483866195223384171,
    1483866195223384167,
]

WELCOME_MESSAGE = (
    " \n"
    "# १९      .    Witaj w ***__NYC__***, {user} .    +\n"
    "-# .⠀⠀⠀⠀ ⠀ •⠀ ⠀ ⠀⠀•⠀ ⠀ ⠀⠀•⠀⠀ ⠀ ⠀⠀⠀⠀don't⠀⠀ dream⠀⠀ it's⠀ ⠀o̲v̲e̲r̲\n"
    "\u200b\n"
    " •⠀ ⠀ ⠀⠀•⠀ ⠀ ⠀⠀•⠀W mieście, które z pozoru nigdy się nie zmienia, a jednak od pewnego czasu coś tu wyraźnie __pęka__.\n"
    "\u200b\n"
    "θৎ . Zanim postawisz pierwszy krok, zapoznaj się z [regulaminem](https://discord.com/channels/1483866194804084768/1483866196490326059). a następnie stwórz swoją postać korzystając ze [wzoru karty postaci](https://discord.com/channels/1483866194804084768/1483866196980924474). Pamiętaj, by uprzednio zarezerwować dla niej wizerunek [męski](https://discord.com/channels/1483866194804084768/1483932486344900689) lub [żeński](https://discord.com/channels/1483866194804084768/1483866197228523647) i pozwól jej wejść w tę historię.\n"
    "\u200b\n"
    "θৎ . Rozgość się na [czacie](https://discord.com/channels/1483866194804084768/1483866195823300608), wszyscy już czekamy! Nie bój się też zadawać [pytań](https://discord.com/channels/1483866194804084768/1483866196490326062).\n"
    "\u200b\n"
    "θৎ . Uważaj tylko, ponieważ w Nowym Jorku każdy coś ukrywa, a niektóre sekrety nie chcą zostać odkryte.\n"
    "\u200b\n"
    "    .             .             .             .              "
)

FAREWELL_MESSAGE = (
    "# १९ . Do zobaczenia w ***__NYC__***, {user_tag} . +\n"
    "-# .⠀⠀⠀⠀ ⠀ •⠀ ⠀ ⠀⠀•⠀ ⠀ ⠀⠀•⠀⠀ ⠀ ⠀⠀⠀⠀some⠀⠀ calls⠀⠀ you⠀ ⠀j̲u̲s̲t̲⠀ ⠀m̲i̲s̲s̲\n"
    "\u200b\n"
    "•⠀ ⠀ ⠀⠀•⠀ ⠀ ⠀⠀•⠀Nie każdy zostaje tu na zawsze, niektórzy odchodzą, zanim historia zdąży się naprawdę zacząć.\n"
    "\u200b\n"
    "θৎ . Dziękujemy, że byłeś częścią tej przestrzeni, nawet jeśli tylko przez chwilę. Nowy Jork zapamiętuje więcej, niż pokazuje, a niektóre ślady nie znikają tak łatwo.\n"
    "\u200b\n"
    "θৎ . Może kiedyś znów odbierzesz to połączenie, a może... tym razem pozwolisz mu przegapić siebie.\n"
    "\u200b\n"
    "    .             .             .             .              "
)


class Powitanie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Zmień nick
        try:
            expiry_date = member.joined_at + timedelta(days=7)
            date_str = expiry_date.strftime("%d.%m.%Y")
            await member.edit(nick=f"౨ৎ  .  {member.name}  {date_str}  .ᐟ")
        except discord.Forbidden:
            pass

        # Nadaj automatyczne role
        roles = []
        for role_id in AUTO_ROLE_IDS:
            role = member.guild.get_role(role_id)
            if role:
                roles.append(role)
        if roles:
            try:
                await member.add_roles(*roles)
            except discord.Forbidden:
                pass

        # Wyślij wiadomość powitalną
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return
        await channel.send(
            WELCOME_MESSAGE.format(user=member.mention),
            file=discord.File("welcome.png")
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return
        await channel.send(
            FAREWELL_MESSAGE.format(user_tag=str(member))
        )


async def setup(bot):
    await bot.add_cog(Powitanie(bot))