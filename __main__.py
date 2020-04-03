import discord
import config
from kambot import Kambot
from music import Music
from core import Core

bot = Kambot(command_prefix=',')

bot.add_cog(Core(bot))
bot.add_cog(Music(bot))

bot.run(config.token)
