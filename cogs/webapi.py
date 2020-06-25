import asyncio
import discord
from modules.api import get_youtube_videos, get_touhouwiki_query

from discord.ext import commands
from modules.pagination import Pagination

class WebApi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yt"])
    @commands.cooldown(1, 2, commands.cooldowns.BucketType.guild)
    async def youtube(self, ctx: commands.Context, *, query: str):
        """Search for a youtube video"""

        async with ctx.channel.typing():
            data = await get_youtube_videos(query, 5)

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


    @commands.command(aliases=["thw"])
    @commands.cooldown(1, 2, commands.cooldowns.BucketType.guild)
    async def touhouwiki(self, ctx: commands.Context, *, query: str):
        """Search a page on the touhou wiki"""

        async with ctx.channel.typing():
            data = await get_touhouwiki_query(query)

            if not data:
                return await ctx.send("Couldn't retrieve any data.")

        if not "query" in data:
            return await ctx.send("Couldn't find any results for this query.")

        item_container = data["query"]["pages"] # container with found pages
                
        pages = [] # message pages will be stored here
        for item in item_container:
            pages.append(item_container[item]["fullurl"])
        
        # Providing the message
        p = Pagination(ctx, pages)
        p.create_task()


    @youtube.error
    async def youtube_error(self, ctx, error):
        if error:
            await ctx.send("Something went wrong...")


def setup(bot):
    bot.add_cog(WebApi(bot))

