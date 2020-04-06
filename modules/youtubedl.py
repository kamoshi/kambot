import youtube_dl
import asyncio
import discord

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
    def __init__(self, ctx: discord.ext.commands.Context, source: discord.FFmpegPCMAudio, *, data, volume=0.5):
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
    async def from_url(cls, ctx: discord.ext.commands.Context, url: str, *, loop=None, stream=False):
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