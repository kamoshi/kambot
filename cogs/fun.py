import random
import discord
from discord.ext import commands

class Fun(commands.Cog):
    
    @commands.command(aliases=["coin", "flip"])
    async def coinflip(self, ctx):
        options = ["Tails", "Heads"]
        await ctx.send(random.choice(options))

    @commands.command(name="choose")
    async def choose(self, ctx, *vargs):
        embed = discord.Embed(
            title="Choose",
            description="Choices: {}\nChosen: **{}**".format(str(vargs), random.choice(vargs)),
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))