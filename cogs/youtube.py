import re
import asyncio
import aiohttp
import discord
from discord.ext import commands
import config

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yt"])
    @commands.cooldown(1, 2, commands.cooldowns.BucketType.guild)
    async def youtube(self, ctx: commands.Context, *, query: str):
        """Search for a youtube video"""

        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                
                youtube_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={query}&type=video&key={config.YOUTUBE_API_KEY}'
                async with session.get(youtube_url) as response:
                    yt_json = await response.json()

                item = yt_json["items"][0]

                if item:
                    await ctx.send("https://www.youtube.com/watch?v=%s" % item["id"]["videoId"])
                else:
                    await ctx.send("Couldn't find any videos.")

    @youtube.error
    async def youtube_error(self, ctx, error):
        if error:
            ctx.send("Something went wrong...")


def setup(bot):
    bot.add_cog(Youtube(bot))

