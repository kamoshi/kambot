"""
Commands in this module:
 - hi
 - TODO: pfp
 - TODO: info
"""

import discord
from discord.ext import commands

class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx):
        await ctx.send("Hello, %s!" % ctx.author.name)

    @commands.command(aliases=["pfp"])
    async def avatar(self, ctx: commands.Context, *, arg: discord.Member):
        embed: discord.Embed = discord.Embed(
            color=discord.Color.blurple(),
            description="[link]({})".format(arg.avatar_url),
            title="{}'s avatar".format(arg.display_name)
        )
        embed.set_image(url=arg.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Core(bot))