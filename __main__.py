import discord
import config
from kambot import Kambot
from cogs import core, music_other

bot = Kambot(command_prefix=',')

bot.add_cog(core.Core(bot))
bot.add_cog(music_other.Music(bot))

bot.run(config.token)
