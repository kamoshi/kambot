import discord
import config
from music import Music

from discord.ext.commands import Bot

bot = Bot(command_prefix=',')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

# bot.add_cog(cogs.core.Core)
bot.add_cog(Music(bot))
bot.run(config.token)
