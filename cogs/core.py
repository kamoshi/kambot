from discord.ext import commands

class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx):
        await ctx.send("Hello, %s!" % ctx.author.name)

def setup(bot):
    bot.add_cog(Core(bot))