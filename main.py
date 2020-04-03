import discord
import os
import config

from discord.ext.commands import Bot
from music import Music

bot = Bot(command_prefix=']')
token = os.environ.get('KAMBOT')

@bot.command()
async def hi(ctx):
    await ctx.send("Hello, %s!" % ctx.author.name)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Music(bot))
bot.run(config.token)
