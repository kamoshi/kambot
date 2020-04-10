import random
import discord
from discord.ext import commands

class Fun(commands.Cog):
    
    @commands.command(aliases=["coin", "flip"])
    async def coinflip(self, ctx):
        """Flips a virtual coin and provides the result."""

        options = ["Tails", "Heads"]
        await ctx.send(random.choice(options))

    @commands.command(name="choose")
    async def choose(self, ctx, *vargs):
        """Chooses a random thing from a list of items."""

        embed = discord.Embed(
            title="Choose",
            description="Choices: {}\nChosen: **{}**".format(str(vargs), random.choice(vargs)),
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))