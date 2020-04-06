import asyncio
import discord
import modules.youtube as yt

from discord.ext import commands
from modules.pagination import Pagination

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yt"])
    @commands.cooldown(1, 2, commands.cooldowns.BucketType.guild)
    async def youtube(self, ctx: commands.Context, *, query: str):
        """Search for a youtube video"""

        async with ctx.channel.typing():
            data = await yt.get_youtube_videos(query, 5)

            if not data:
                return await ctx.send("Couldn't retrieve any data.")

        item_container = data["items"] # container with video data
        item_count = len(item_container)  # number of items

        if item_count  == 0:
            return await ctx.send("Couldn't find any videos.")
                
        pages = [] # message pages will be stored here
        for item in item_container:
            pages.append("https://www.youtube.com/watch?v=%s" % item["id"]["videoId"])
        
        # Providing the message
        p = Pagination(ctx, pages)
        p.create_task()
                    

    @youtube.error
    async def youtube_error(self, ctx, error):
        if error:
            await ctx.send("Something went wrong...")


def setup(bot):
    bot.add_cog(Youtube(bot))

