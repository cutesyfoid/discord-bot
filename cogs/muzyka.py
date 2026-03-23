import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
import random
import time
import config

YTDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}

YTDL_SEARCH_OPTS = {
    "quiet": True,
    "default_search": "ytsearch5",
    "noplaylist": True,
    "extract_flat": True,
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTS)
ytdl_search = yt_dlp.YoutubeDL(YTDL_SEARCH_OPTS)


class MusicSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("webpage_url")
        self.duration = data.get("duration", 0)
        self.thumbnail = data.get("thumbnail")

    @classmethod
    async def from_url(cls, url, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
        if "entries" in data:
            data = data["entries"][0]
        return cls(discord.FFmpegPCMAudio(data["url"], **FFMPEG_OPTS), data=data)


def fmt_duration(seconds):
    if not seconds:
        return "?"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class Muzyka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.loop_song = {}
        self.loop_queue = {}
        self.current = {}
        self.start_time = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queue:
            self.queue[guild_id] = []
        return self.queue[guild_id]

    def check_dj(self, interaction):
        if config.DJ_ROLE_ID == 0:
            return True
        role = interaction.guild.get_role(config.DJ_ROLE_ID)
        return role in interaction.user.roles

    async def play_next(self, guild_id, voice_client):
        q = self.get_queue(guild_id)
        if self.loop_song.get(guild_id) and self.current.get(guild_id):
            source = await MusicSource.from_url(self.current[guild_id].url, loop=self.bot.loop)
            self.current[guild_id] = source
        elif q:
            source = q.pop(0)
            if self.loop_queue.get(guild_id) and self.current.get(guild_id):
                try:
                    s = await MusicSource.from_url(self.current[guild_id].url, loop=self.bot.loop)
                    q.append(s)
                except Exception:
                    pass
            self.current[guild_id] = source
        else:
            self.current[guild_id] = None
            return

        self.start_time[guild_id] = time.time()
        voice_client.play(
            self.current[guild_id],
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(guild_id, voice_client), self.bot.loop
            )
        )

    async def search_youtube(self, query: str):
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl_search.extract_info(f"ytsearch5:{query}", download=False)
        )
        if "entries" in data:
            return data["entries"][:5]
        return []

    @app_commands.command(name="play", description="Odtwórz muzykę z YouTube")
    @app_commands.describe(query="Nazwa lub link YouTube")
    async def play(self, interaction: discord.Interaction, query: str):
        if not self.check_dj(interaction):
            await interaction.response.send_message("Potrzebujesz roli DJ!", ephemeral=True)
            return
        if not interaction.user.voice:
            await interaction.response.send_message("Wejdź na kanał głosowy!", ephemeral=True)
            return
        await interaction.response.defer()
        vc = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect()
        source = await MusicSource.from_url(query, loop=self.bot.loop)
        q = self.get_queue(interaction.guild_id)
        if vc.is_playing() or vc.is_paused():
            q.append(source)
            await interaction.followup.send(embed=discord.Embed(
                title="Dodano do kolejki",
                description=f"[{source.title}]({source.url})\nPozycja: **#{len(q)}** | Czas: {fmt_duration(source.duration)}",
                color=0x9b59b6
            ))
        else:
            self.current[interaction.guild_id] = source
            self.start_time[interaction.guild_id] = time.time()
            q.insert(0, source)
            await self.play_next(interaction.guild_id, vc)
            await interaction.followup.send(embed=discord.Embed(
                title="Teraz gra",
                description=f"[{source.title}]({source.url})\nCzas: {fmt_duration(source.duration)}",
                color=0x9b59b6
            ).set_thumbnail(url=source.thumbnail or ""))

    @play.autocomplete("query")
    async def play_autocomplete(self, interaction: discord.Interaction, current: str):
        if len(current) < 2:
            return []
        results = await self.search_youtube(current)
        return [
            app_commands.Choice(
                name=r.get("title", "?")[:100],
                value=r.get("url") or r.get("webpage_url") or current
            )
            for r in results if r.get("title")
        ]

    @app_commands.command(name="pause", description="Pauzuj muzykę")
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("Zapauzowano.")
        else:
            await interaction.response.send_message("Nic nie gra.", ephemeral=True)

    @app_commands.command(name="resume", description="Wznów muzykę")
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("Wznowiono.")
        else:
            await interaction.response.send_message("Muzyka nie jest zapauzowana.", ephemeral=True)

    @app_commands.command(name="skip", description="Pomiń obecny utwór")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("Pominięto!")
        else:
            await interaction.response.send_message("Nic nie gra.", ephemeral=True)

    @app_commands.command(name="stop", description="Zatrzymaj muzykę i rozłącz bota")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            self.get_queue(interaction.guild_id).clear()
            self.loop_song[interaction.guild_id] = False
            self.loop_queue[interaction.guild_id] = False
            await vc.disconnect()
            await interaction.response.send_message("Zatrzymano i rozłączono.")
        else:
            await interaction.response.send_message("Bot nie jest na kanale.", ephemeral=True)

    @app_commands.command(name="loop", description="Zapętl obecny utwór")
    async def loop(self, interaction: discord.Interaction):
        gid = interaction.guild_id
        self.loop_song[gid] = not self.loop_song.get(gid, False)
        self.loop_queue[gid] = False
        status = "włączony" if self.loop_song[gid] else "wyłączony"
        await interaction.response.send_message(f"Loop piosenki: **{status}**")

    @app_commands.command(name="loopqueue", description="Zapętl całą kolejkę")
    async def loopqueue(self, interaction: discord.Interaction):
        gid = interaction.guild_id
        self.loop_queue[gid] = not self.loop_queue.get(gid, False)
        self.loop_song[gid] = False
        status = "włączony" if self.loop_queue[gid] else "wyłączony"
        await interaction.response.send_message(f"Loop kolejki: **{status}**")

    @app_commands.command(name="shuffle", description="Przetasuj kolejkę")
    async def shuffle(self, interaction: discord.Interaction):
        q = self.get_queue(interaction.guild_id)
        if not q:
            await interaction.response.send_message("Kolejka jest pusta!", ephemeral=True)
            return
        random.shuffle(q)
        await interaction.response.send_message("Kolejka przetasowana!")

    @app_commands.command(name="nowplaying", description="Pokaż co teraz gra")
    async def nowplaying(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        gid = interaction.guild_id
        source = self.current.get(gid)
        if not vc or not (vc.is_playing() or vc.is_paused()) or not source:
            await interaction.response.send_message("Nic nie gra.", ephemeral=True)
            return
        elapsed = int(time.time() - self.start_time.get(gid, time.time()))
        duration = source.duration or 0
        bar_len = 20
        filled = min(int(bar_len * elapsed / duration) if duration else 0, bar_len)
        bar = "▬" * filled + "🔘" + "▬" * (bar_len - filled)
        loop_status = ""
        if self.loop_song.get(gid):
            loop_status = " | Loop: piosenka"
        elif self.loop_queue.get(gid):
            loop_status = " | Loop: kolejka"
        e = discord.Embed(
            title="Teraz gra",
            description=f"[{source.title}]({source.url})\n\n{bar}\n`{fmt_duration(elapsed)}` / `{fmt_duration(duration)}`{loop_status}",
            color=0x9b59b6
        )
        if source.thumbnail:
            e.set_thumbnail(url=source.thumbnail)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="seek", description="Przewiń do konkretnego miejsca")
    @app_commands.describe(sekundy="Czas w sekundach")
    async def seek(self, interaction: discord.Interaction, sekundy: int):
        vc = interaction.guild.voice_client
        gid = interaction.guild_id
        source = self.current.get(gid)
        if not vc or not source:
            await interaction.response.send_message("Nic nie gra.", ephemeral=True)
            return
        await interaction.response.defer()
        vc.stop()

        # pobierz swiezy URL
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(source.url, download=False)
        )
        if "entries" in data:
            data = data["entries"][0]
        fresh_url = data["url"]

        new_source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                fresh_url,
                before_options=f"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {sekundy}",
                options="-vn"
            )
        )
        new_source.title = source.title
        new_source.url = source.url
        new_source.duration = source.duration
        new_source.thumbnail = source.thumbnail
        new_source.data = data
        self.start_time[gid] = time.time() - sekundy
        self.current[gid] = new_source
        vc.play(
            new_source,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(gid, vc), self.bot.loop
            )
        )
        await interaction.followup.send(f"Przewinięto do `{fmt_duration(sekundy)}`")

    @app_commands.command(name="remove", description="Usuń utwór z kolejki")
    @app_commands.describe(pozycja="Numer pozycji w kolejce")
    async def remove(self, interaction: discord.Interaction, pozycja: int):
        q = self.get_queue(interaction.guild_id)
        if pozycja < 1 or pozycja > len(q):
            await interaction.response.send_message("Nieprawidłowa pozycja!", ephemeral=True)
            return
        removed = q.pop(pozycja - 1)
        await interaction.response.send_message(embed=discord.Embed(
            title="Usunięto z kolejki",
            description=f"[{removed.title}]({removed.url})",
            color=0xe74c3c
        ))

    @app_commands.command(name="queue", description="Pokaż kolejkę")
    async def show_queue(self, interaction: discord.Interaction):
        q = self.get_queue(interaction.guild_id)
        vc = interaction.guild.voice_client
        source = self.current.get(interaction.guild_id)
        if not source and not q:
            await interaction.response.send_message("Kolejka jest pusta.", ephemeral=True)
            return
        desc = ""
        if source:
            desc += f"**Teraz:** [{source.title}]({source.url}) `{fmt_duration(source.duration)}`\n\n"
        for i, s in enumerate(q[:15], 1):
            desc += f"`{i}.` [{s.title}]({s.url}) `{fmt_duration(s.duration)}`\n"
        if len(q) > 15:
            desc += f"\n...i {len(q)-15} więcej"
        e = discord.Embed(title="Kolejka", description=desc or "Pusta", color=0x9b59b6)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="volume", description="Zmień głośność (0-100)")
    @app_commands.describe(poziom="Głośność 0-100")
    async def volume(self, interaction: discord.Interaction, poziom: int):
        vc = interaction.guild.voice_client
        if vc and vc.source:
            vc.source.volume = max(0, min(poziom, 100)) / 100
            await interaction.response.send_message(f"Głośność: **{poziom}%**")
        else:
            await interaction.response.send_message("Nic nie gra.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Muzyka(bot))