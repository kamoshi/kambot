import re
import asyncio
import aiohttp
import discord
import async_timeout
from discord.ext import commands
import config


class Pagination:

    def __init__(self, ctx: commands.Context, pages: list, starting_page=0, time_limit=10):
        self.ctx = ctx  # context taken from command
        self.pages = pages
        self.current_page = starting_page
        self.time_limit = time_limit

    async def handle_message(self):
        msg = await self.ctx.send(self.pages[self.current_page])

        emoji_list = ['⬅️', '➡️', '⏹️']  # These buttons we use
        
        # Predicate
        def check(reaction: discord.Reaction, user):
            return reaction.message.id == msg.id and user == self.ctx.message.author and str(reaction.emoji) in emoji_list

        await self.create_emoji(msg, emoji_list)  # add emoji to message
        
        # Loop that checks for reactions
        while True:
            try:
                # returns a tuple (reaction, user), we just need reaction
                reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.time_limit, check=check)
                emoji = reaction.emoji

                if emoji == '⬅️': # BACK
                    if self.current_page == 0:
                        self.current_page = len(self.pages)
                    self.current_page = self.current_page -1 # go back
                    await msg.remove_reaction('⬅️', user)

                elif emoji == '➡️': # FORWARD
                    self.current_page = self.current_page +1 # go forwards
                    if self.current_page == len(self.pages):
                        self.current_page = 0
                    await msg.remove_reaction('➡️', user)

                elif emoji == '⏹️': # STOP REACTIONS
                    return await self.clear_emoji(msg, emoji_list)

                new_content = "{}/{} {}".format((self.current_page+1), len(self.pages), self.pages[self.current_page])
                await msg.edit(content=new_content)

            except asyncio.TimeoutError:
                return await self.clear_emoji(msg, emoji_list)


    async def clear_emoji(self, msg: discord.Message, emoji_list: list):
        """Fill the mesage with reaction menu"""
        try:
            for reaction in emoji_list:
                await msg.clear_reaction(reaction)
        except Exception:
            return

    async def create_emoji(self, msg: discord.Message, emoji_list: list):
        """Remove the reaction menu"""
        try:
            for reaction in emoji_list:
                await msg.add_reaction(reaction)
        except Exception:
            return


class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yt"])
    @commands.cooldown(1, 2, commands.cooldowns.BucketType.guild)
    async def youtube(self, ctx: commands.Context, *, query: str):
        """Search for a youtube video"""

        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                
                youtube_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q={query}&type=video&key={config.YOUTUBE_API_KEY}'
                async with session.get(youtube_url) as response:
                    yt_json = await response.json()

                if not yt_json:
                    return await ctx.send("Couldn't retrieve any data.")

                item_container = yt_json["items"] # container with video data
                item_count = len(item_container)  # number of items

                if item_count  == 0:
                    return await ctx.send("Couldn't find any videos.")
                
                pages = [] # message pages will be stored here
                for item in item_container:
                    pages.append("https://www.youtube.com/watch?v=%s" % item["id"]["videoId"])
        
        # Providing the message
        p = Pagination(ctx, pages)
        self.bot.loop.create_task(p.handle_message())
                    

    @youtube.error
    async def youtube_error(self, ctx, error):
        if error:
            await ctx.send("Something went wrong...")


def setup(bot):
    bot.add_cog(Youtube(bot))

