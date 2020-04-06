import discord

from discord.ext import commands
from discord.ext.commands import Context
from modules.music import VoiceController
from modules.youtubedl import YTDLSource

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.voice_controllers = {}

    def get_voice_controller(self, ctx: Context):
        """Find the proper voice_state for a given command"""

        state = self.voice_controllers.get(ctx.guild.id)
        if not state:
            state = VoiceController(self.bot, ctx)
            self.voice_controllers[ctx.guild.id] = state
        return state


    @commands.command()
    async def join(self, ctx: Context):
        """Joins a voice channel"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            controller = self.get_voice_controller(ctx)
            await controller.connect_to_channel(channel)
            await ctx.send("Connected to channel {}".format(channel.name))

        else:
            await ctx.send("You're not in any voice channel")


    @commands.command()
    async def play(self, ctx: Context, *, url: str):
        """Plays from a url (almost anything youtube_dl supports)"""

        if not ctx.voice_client:  # if not in voice chat, treat this as if user asked to join
            if ctx.author.voice:
                await ctx.invoke(self.join)
            else:
                return await ctx.send("You're not in any voice channel")

        async with ctx.typing():
            song = await YTDLSource.from_url(ctx, url, loop=self.bot.loop, stream=True)
            controller = self.get_voice_controller(ctx)

            await controller.add_song(song)
            await ctx.send("Added song {}".format(song.title))


    @commands.command()
    async def stop(self, ctx: Context):
        """Quit voice chat (in the future clear queue too)"""
        if not ctx.voice_client:
            return await ctx.send("Bot is not playing any songs at the moment.")

        controller = self.get_voice_controller(ctx)
        await controller.stop_player()

    
    @commands.command()
    async def queue(self, ctx: Context):
        """Show the queue of the bot"""

        if ctx.voice_client:
            controller = self.get_voice_controller(ctx)

            if controller.queue.qsize() == 0:
                return await ctx.send('Empty queue.')

            else:
                queue = ""
                i = 1
                for song in controller.queue._queue:
                    queue += '{0}. **{1.title}**\n'.format(i, song)
                    i += 1

                embed = discord.Embed( description='**{0} tracks:**\n\n{1}'.format(controller.queue.qsize(), queue) )
                await ctx.send(embed=embed)

        else:
            await ctx.send("Bot is not playing any songs at the moment.")


def setup(bot):
    bot.add_cog(Music(bot))