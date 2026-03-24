# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import asyncio

TRIGGER_CHANNEL_ID = 1483866196980924475
TRIGGER_WORD = "muzeum"

WATKI = [
    {
        "thread_id": 1486009094593581097,
        "obrazek":   "muzeum.png",
        "wiadomosc": (
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀    \n"
            "       ⠀ ⠀⁭\n"
            "# .ㅤ                         ・・  𝐌𝐄𝐓𝐑𝐎𝐏𝐎𝐋𝐈𝐓𝐀𝐍    𝐌𝐔𝐒𝐄𝐔𝐌    𝑂𝐹      𝐀𝐑𝐓.    .    .\n"
            "-# .                                                                                  opis     miejsca     pracy\n"
            " ㅤ\n"
            "⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀       \n"
            "    ⠀ ⠀⁭\n"
            "  〻 𝟏.𝟏⠀.          ⠀⠀    ⠀⠀Praca w Metropolitan Museum of Art to wyjątkowe doświadczenie dla osób, które chcą być częścią miejsca owianego tajemnicą i niepowtarzalną atmosferą. To właśnie tutaj pracują ludzie odpowiedzialni za bezpieczeństwo, porządek i wrażenia odwiedzających — od ochrony, przez osoby dbające o teren, aż po przewodników. Każdy pracownik przechodzi staranny i bardzo dokładny proces rekrutacji prowadzony osobiście przez rodzinę (tu nazwisko rodziny). Kandydaci są szczegółowo weryfikowani, analizowana jest nie tylko ich kariera, ale także przeszłość i wszystkie istotne aspekty życia. Nic nie pozostaje przypadkowe, a każdy element ich historii zostaje dokładnie sprawdzony, zanim zostaną dopuszczeni do pracy w, jak można łatwo przyznać, tak odpowiedzialnym miejscu.\n"
            "\n"
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀           ⠀ ⠀⁭"
        ),
    },
    {
        "thread_id": 1486010144914542642,
        "obrazek":   "studenci.png",
        "wiadomosc": (
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀           ⠀ ⠀⁭\n"
            "\n"
            "# .ㅤ                         ・・  𝐂𝐎𝐋𝐔𝐌𝐁𝐈𝐀     𝐔𝐍𝐈𝐕𝐄𝐑𝐒𝐈𝐓𝐘     𝐒𝐓𝐔𝐃𝐄𝐍𝐓𝐒.    .    .\n"
            "-# .                                                                                  opis     funkcji\n"
            " ㅤ\n"
            "⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀       \n"
            "    ⠀ ⠀⁭\n"
            "   〻  ⠀.          ⠀⠀    ⠀⠀Jeśli widzisz swoją przyszłość w medycynie, interesują cię zagadnienia związane z ekonomią albo funkcjonowaniem państwa, a może rozważasz karierę w zawodach prawniczych, takich jak prokurator, adwokat czy sędzia — Columbia University może być dla ciebie świetnym wyborem. To miejsce daje ogromne możliwości rozwoju i pozwala poznać inspirujących ludzi, z którymi relacje mogą przetrwać całe życie. Nie bez powodu mówi się, że okres studiów to jeden z najbardziej wyjątkowych i wartościowych etapów w życiu.\n"
            "\n"
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀           ⠀ ⠀⁭"
        ),
    },
    {
        "thread_id": 1486010267430031400,
        "obrazek":   "profesorowi.png",
        "wiadomosc": (
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀          \n"
            " ⠀ ⠀⁭\n"
            "# .ㅤ                         ・・  𝐂𝐎𝐋𝐔𝐌𝐁𝐈𝐀     𝐔𝐍𝐈𝐕𝐄𝐑𝐒𝐈𝐓𝐘     𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐎𝐑𝐒.    .    .\n"
            "-# .                                                                                  opis     funkcji\n"
            " ㅤ\n"
            "⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀\n"
            "    ⠀ ⠀⁭\n"
            "   〻  ⠀.          ⠀⠀    ⠀⠀Jeśli fascynuje cię dzielenie się wiedzą, prowadzenie badań i inspirowanie innych do rozwoju, praca profesora na Columbia University może być dla ciebie idealną ścieżką. To tutaj masz możliwość rozwijać swoje pasje naukowe, współpracować z wybitnymi specjalistami i kształcić kolejne pokolenia ambitnych studentów. Każdy dzień to nowe wyzwania, ciekawe projekty i szansa na realny wpływ na świat nauki. Nie bez powodu mówi się, że praca na uczelni to nie tylko zawód, ale również styl życia pełen inspiracji i ciągłego rozwoju. \n"
            "\n"
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀"
        ),
    },
    {
        "thread_id": 1486010386955108605,
        "obrazek":   "medycyna.png",
        "wiadomosc": (
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀        ⠀ ⠀⁭\n"
            "# .ㅤ                         ・・  𝐌𝐄𝐃𝐈𝐂𝐀𝐋        𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐈𝐎𝐍𝐒.    .    .\n"
            "-# .                                                                                  opis     funkcji\n"
            "⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀    ⠀ ⠀\n"
            "   〻  ⠀.          ⠀⠀    ⠀⠀Praca w medycynie to ogromna odpowiedzialność, ale też wyjątkowa szansa na rozwój i zdobywanie bezcennego doświadczenia. Wielu lekarzy, chirurgów i pielęgniarek, którzy każdego dnia ratują życie pacjentów, to absolwenci Columbia University — uczelni, która przygotowuje do pracy na najwyższym poziomie. To środowisko pełne wyzwań, gdzie liczy się nie tylko wiedza i precyzja, ale także empatia oraz umiejętność pracy pod presją. Nowoczesne szpitale, dostęp do najnowszych technologii i współpraca z wybitnymi specjalistami sprawiają, że każdy dzień przynosi nowe doświadczenia, i możliwość realnego wpływu na życie innych ludzi.\n"
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀"
        ),
    },
    {
        "thread_id": 1486010456232693830,
        "obrazek":   "prawo.png",
        "wiadomosc": (
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀        ⠀ ⠀⁭\n"
            "# .ㅤ                         ・・  𝐖𝐎𝐑𝐊𝐈𝐍𝐆        𝐈𝐍        𝐋𝐀𝐖.    .    .\n"
            "-# .                                                                                  opis     funkcji\n"
            "⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀    ⠀ ⠀\n"
            "   〻  ⠀.          ⠀⠀    ⠀⠀Praca w branży prawniczej w Nowym Jorku to wymagająca, ale niezwykle prestiżowa ścieżka kariery. Wielu prawników, prokuratorów czy sędziów rozpoczynało swoją drogę jako studenci Columbia University, gdzie zdobywali wiedzę i umiejętności potrzebne do pracy na najwyższym poziomie. To środowisko, w którym liczy się nie tylko doskonała znajomość prawa, ale także analityczne myślenie, odporność na stres i umiejętność podejmowania trudnych decyzji. Każdy dzień przynosi nowe wyzwania, od reprezentowania klientów, przez analizowanie skomplikowanych spraw, aż po udział w ważnych postępowaniach sądowych. To miejsce dla ludzi, którzy trzymają swoje nerwy na wodzy.\n"
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀"
        ),
    },
    {
        "thread_id": 1486010550319055178,
        "obrazek":   "biznes.png",
        "wiadomosc": (
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀        ⠀ ⠀⁭\n"
            "# .ㅤ                         ・・  𝐖𝐎𝐑𝐊𝐈𝐍𝐆       𝐈𝐍       𝐁𝐔𝐒𝐈𝐍𝐄𝐒𝐒.    .    .\n"
            "-# .                                                                                  opis     funkcji\n"
            "⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀    ⠀ ⠀\n"
            "   〻  ⠀.          ⠀⠀    ⠀⠀Praca w biznesie to dynamiczne i wymagające środowisko, w którym codzienność wyznaczają szybkie decyzje, ambitne cele i nieustanny rozwój. To właśnie tutaj znajdują się biura wielkich korporacji, potężnych firm i rozpoznawalnych na całym świecie marek. To przestrzeń dla osób, które chcą działać na dużą skalę, podejmować strategiczne decyzje i mieć realny wpływ na gospodarkę. Liczy się tu nie tylko wiedza i doświadczenie, ale także kreatywność, umiejętność pracy w zespole oraz odnajdywanie się w szybko zmieniających się warunkach. Każdy dzień to nowe projekty, spotkania i wyzwania, które mogą otworzyć drzwi do międzynarodowej kariery. \n"
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀"
        ),
    },
    {
        "thread_id": 1486010702354317402,
        "obrazek":   "stroz.png",
        "wiadomosc": (
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀        ⠀ ⠀⁭\n"
            "# .ㅤ                         ・・  𝐋𝐀𝐖       𝐄𝐍𝐅𝐎𝐑𝐂𝐄𝐑𝐒.    .    .\n"
            "-# .                                                                                  opis     funkcji\n"
            "⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀    ⠀ ⠀\n"
            "   〻  ⠀.          ⠀⠀    ⠀⠀Praca w służbach porządkowych w Nowym Jorku to wymagające i odpowiedzialne zajęcie, w którym każdy dzień przynosi nowe wyzwania. Policjanci, detektywi, strażnicy miejscy i inni funkcjonariusze dbają o bezpieczeństwo mieszkańców, utrzymanie porządku oraz rozwiązywanie spraw kryminalnych. W tej pracy możesz wybrać różne ścieżki, ponieważ możesz angażować się w poważne śledztwa w dziale narkotykowym, prowadzić działania operacyjne i ścigać przestępców, albo zająć się bardziej rutynowymi obowiązkami, takimi jak wystawianie mandatów za wykroczenia drogowe. Każda z tych ról jest ważna i wymaga zaangażowania, bo do prawidłowego funkcjonowania służb potrzebni są pracownicy na wszystkich poziomach odpowiedzialności.  \n"
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀"
        ),
    },
    {
        "thread_id": 1486010751150723202,
        "obrazek":   "inne.png",
        "wiadomosc": (
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀        ⠀ ⠀⁭\n"
            "# .ㅤ                         ・・  𝐎𝐓𝐇𝐄𝐑 .    .    .\n"
            "-# .                                                                                  opis     funkcji\n"
            "⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀    ⠀ ⠀\n"
            "   〻  ⠀.          ⠀⠀    ⠀⠀Oczywiście, w każdej społeczności miasta potrzebni są także pracownicy w bardziej „codziennych" zawodach. Kawiarnie szukają baristów, w klubach i barach brakuje kelnerów i DJ-ów, a pobliskie kwiaciarnie potrzebują osób do przygotowywania i pakowania prezentów. A jeśli marzysz o własnym biznesie, to droga stoi przed tobą otworem. Nam pozostało życzyć Ci powodzenia i sukcesów w realizacji planów. \n"
            "ㅤ⠀      ·⠀⠀ ⠀       ⠀⠀   ·⠀⠀            ⠀ ⠀·⠀⠀"
        ),
    },
]


class Muzeum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.id != TRIGGER_CHANNEL_ID:
            return
        if message.content.strip().lower() != TRIGGER_WORD:
            return
        if self.running:
            return

        self.running = True
        try:
            for watek_data in WATKI:
                thread = self.bot.get_channel(watek_data["thread_id"])
                if thread is None:
                    try:
                        thread = await self.bot.fetch_channel(watek_data["thread_id"])
                    except Exception:
                        continue

                obrazek = watek_data["obrazek"]

                await thread.send(file=discord.File(obrazek))
                await asyncio.sleep(0.7)

                await thread.send(file=discord.File("przerywnik_1.png"))
                await asyncio.sleep(0.7)

                await thread.send(watek_data["wiadomosc"])
                await asyncio.sleep(0.7)

                await thread.send(file=discord.File("przerywnik_1.png"))
                await asyncio.sleep(0.7)

                await thread.send(file=discord.File(obrazek))
                await asyncio.sleep(0.7)

        except Exception as e:
            print(f"[Muzeum] Błąd: {e}")
        finally:
            self.running = False


async def setup(bot):
    await bot.add_cog(Muzeum(bot))