import discord
import asyncio
import async_timeout

from modules.youtubedl import YTDLSource
from discord.ext import commands

class PlaybackException(Exception):
    pass

class VoiceController:
    """
    Class controlls the voicechat activity for a single discord
    Each discord guild should have *its own* controller, only one
    """
    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        self.bot = bot      # Bot which is controlled by this controller
        self.guild = guild  # Guild for which this controller is responsible
        
        self.queue = asyncio.Queue()                    # Queue with songs in some order
        self.finished: asyncio.Event = asyncio.Event()  # Event triggered when a song is finished playing
        self.finished.set()

        self.current_song = None  # currently playing song
        self.current_task = bot.loop.create_task(self.player_task())  # this should contain a task responsible for keeping the music playing

    def __del__(self):
        if self.current_task:
            self.current_task.cancel() # When the controller is removed, task should be cancelled


    async def stop_player(self):
        """This function is responsible for stopping the player and clearing queue"""
        if self.current_task:
            self.current_task.cancel()  # Task is cancelled
            self.current_task = None

        self.current_song = None
        self.queue._queue.clear()  # Clear the queue
        self.finished.set()  # Set flag finished to true, because technically it's finished

        voice = self.guild.voice_client
        if voice:
            voice.disconnect()
    

    async def player_task(self):
        """This function is responsible for keeping the music playing as long as required"""
        
        while True:

            if not self.guild.voice_client:
                return

            await self.finished.wait()  # wait until player finished a song

            try:  # Trying to get next song to play
                async with async_timeout.timeout(180):
                    self.current_song = await self.queue.get()
            except asyncio.TimeoutError:  # Failed to get a song
                return self.bot.loop.create_task(self.stop_player())  # we are stopping

            if self.guild.voice_client:
                self.guild.voice_client.play(self.current_song.data, after=self.song_finished())  # callback
                await self.current_song.ctx.send(embed=self.current_song.create_embed())  # SEND AN EMBED
            else:
                return self.bot.loop.create_task(self.stop_player())


    async def song_finished(self):
        """This is a callback after a song is finished playing"""
        self.finished.set()


    async def skip_song(self):
        """Skip the currently playing song"""
        voice = self.guild.voice_client
        if voice:
            if voice.is_playing():
                voice.stop()


    async def add_song(self, song: YTDLSource):
        voice = self.guild.voice_client
        if voice:
            await self.queue.put(song)

            if not self.current_task or self.current_task.cancelled():
                self.current_task = self.bot.loop.create_task(self.player_task())


    async def connect_to_channel(self, channel: discord.VoiceChannel):
        """Connect to a voice channel in a guild"""
        voice = self.guild.voice_client
        if voice:
            return await voice.move_to(channel)

        else:
            await channel.connect()
