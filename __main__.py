import logging
import discord

import config
from kambot import Kambot

logging.basicConfig(level=logging.INFO)
bot = Kambot(command_prefix=',')

# Load cogs
bot.load_extension("cogs.core")
bot.load_extension("cogs.fun")
bot.load_extension("cogs.polls")
bot.load_extension("cogs.youtube")
bot.load_extension("cogs.music")

bot.run(config.TOKEN)
