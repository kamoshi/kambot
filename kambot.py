from discord.ext.commands import Bot


class Kambot(Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('Logged in as {0} ({0.id})'.format(self.user))
        print('------')