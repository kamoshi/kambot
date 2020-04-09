import discord
import time
from discord.ext.commands import Bot


class Kambot(Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_time = time.time()

    async def on_ready(self):
        print('Logged in as {0} ({0.id})'.format(self.user))
        print('------')
        await self.change_presence(activity=discord.Activity(name=",help :)", type=discord.ActivityType.playing))