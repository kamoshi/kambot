import asyncio
import async_timeout
import discord
import youtube_dl

from discord.ext import commands
from discord.ext.commands import Context

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''




class YTDLSource(discord.PCMVolumeTransformer):
    """
    Class wraps the data obtained from YouTube
    It represents a singular song "unit",
    which can then be kept in a queue
    Args:
        requested_by : Person who requested the song
        channel : Channel where the request was made
        data : youtube data package
        title : title of the video
        url : link to the video
    """

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    # INITIALIZE SONG DATA
    def __init__(self, ctx: Context, source: discord.FFmpegPCMAudio, *, data, volume=0.5):
        super().__init__(source, volume)

        self.requested_by = ctx.author  # Person who requested the song to be
        self.channel = ctx.channel

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        self.thumbnail = data.get('thumbnail')


    def create_embed(self):
        """Generate embed message describing the song"""

        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.duration)
                 .add_field(name='Requested by', value=self.requested_by.name)
                 .add_field(name='Uploader', value='[{0.uploader}]({0.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.url})'.format(self))
                 .set_thumbnail(url=self.thumbnail))

        return embed


    @classmethod
    async def from_url(cls, ctx: Context, url: str, *, loop=None, stream=False):
        """Looks up a video based on a query and returns its data"""
        
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
        return cls(ctx, discord.FFmpegPCMAudio(filename, **cls.FFMPEG_OPTIONS), data=data)


    @classmethod
    async def from_query_get_link(cls, query: str, *, loop=None) -> str:
        """Looks up a video based on a query and returns a link to it"""

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(query, download=False, process=False))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        return data['webpage_url']


    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)




class VoiceState:
    """
    Class represents a state of the voice in a discord guild
    Each discord guild should have its own state
    """
    def __init__(self, bot: commands.Bot, ctx: Context):
        self.bot = bot
        self.ctx = ctx

        self.queue = asyncio.Queue()

        self.finished: asyncio.Event = asyncio.Event()
        self.player_task = bot.loop.create_task(self.create_player_task())

    def __del__(self):
        self.player_task.cancel()

    async def create_player_task(self):
        while True:
            try:
                async with async_timeout.timeout(180):  # keep trying for 3 minutes to get a new song
                    self.current = await self.queue.get()  # get a song
            except asyncio.TimeoutError:  # Failed to get a song
                return self.bot.loop.create_task(self.stop_player())
            
            if self.ctx.voice_client:
                self.ctx.voice_client.play(self.current, after=self.play_next_song)
                await self.ctx.send(embed=self.current.create_embed())  # SEND AN EMBED
            else:
                await self.ctx.send("Something went wrong...")
                return self.bot.loop.create_task(self.stop_player())

            await self.finished.wait()  # wait until player finished a song

    def play_next_song(self, error=None):
        """This function should be a callback after a song is finished"""
        if error:
            raise commands.DiscordException("Playback finished with an error: %s" % str(error))
        self.finished.set()  # Set the finished flag to True

    async def skip_song(self):
        """Skip the currently playing song"""
        voice = self.ctx.voice_client
        if voice:
            if voice.is_playing():
                voice.stop()

    async def stop_player(self):
        """Stop the voice activity, do basic cleanup"""
        self.player_task.cancel()
        self.queue._queue.clear()  # Maybe this isn't a good way to clear it
        voice = self.ctx.voice_client
        if voice:
            await voice.disconnect()
        

    async def add_song(self, song: YTDLSource):
        voice = self.ctx.voice_client
        if voice:
            await self.queue.put(song)
        
        if not self.player_task or self.player_task.cancelled():
            self.player_task = self.bot.loop.create_task(self.create_player_task())


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: Context):
        """Find the proper voice_state for a given command"""

        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    @commands.command()
    async def join(self, ctx: Context):
        """Joins a voice channel"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(channel)

            await channel.connect()
        else:
            await ctx.send("You're not in any voice channel")


    @commands.command()
    async def play(self, ctx: Context, *, url: str):
        """Plays from a url (almost anything youtube_dl supports)"""

        if not ctx.voice_client:  # if not in voice chat, join
            await ctx.invoke(self.join, ctx)

        async with ctx.typing():
            song = await YTDLSource.from_url(ctx, url, loop=self.bot.loop, stream=True)
            voice_state = self.get_voice_state(ctx)

            await voice_state.add_song(song)
            await ctx.send("Added song")


    @commands.command()
    async def stop(self, ctx: Context):
        """Quit voice chat (in the future clear queue too)"""
        voice_state = self.get_voice_state(ctx)
        await voice_state.stop_player()
        await ctx.voice_client.disconnect()


    @commands.command()
    async def yt(self, ctx: Context, *, args: str):
        """Search for video link on youtube"""

        link = await YTDLSource.from_query_get_link(args)
        if link is not None:
            return await ctx.send(link)
        
        await ctx.send("Couldn't find any videos")


    @commands.command()
    async def pause(self, ctx: Context) -> None:
        """Pause the song player"""

        if ctx.voice_client.is_paused():
            return await ctx.send("Player is already paused")
            
        return await ctx.voice_client.pause()


    @commands.command()
    async def resume(self, ctx: Context):
        """Resume the song player"""

        if ctx.voice_client.is_paused():
            return await ctx.voice_client.resume()
        
        return await ctx.send("Player is already playing")

    
    @commands.command()
    async def queue(self, ctx: Context):
        """Show the queue of the bot"""

        if ctx.voice_client:
            voice_state = self.get_voice_state(ctx)
            if voice_state.queue.qsize() == 0:
                return await ctx.send('Empty queue.')
            else:
                queue = ''
                for i, song in enumerate(voice_state.queue._queue):
                    queue += '`{0}.` [**{1.title}**]({1.url})\n'.format(i + 1, song)

                embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format((voice_state.queue.qsize()), queue)))
                await ctx.send(embed=embed)
        else:
            await ctx.send("Not playing music right now...")


    @pause.before_invoke
    @resume.before_invoke
    async def ensure_voice_state(self, ctx: Context) -> None:
        """Invoked before functions that require the bot to be in a voice chat"""

        if ctx.voice_client is None:
            raise commands.CommandError("Bot is not connected to any voice channel")