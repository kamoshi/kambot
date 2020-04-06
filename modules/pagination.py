from discord.ext import commands
import discord
import asyncio

class Pagination:
    """
    Class respinsible for creating interactive message "pages"
    Users can control displayed page by pressing reaction button
    """
    def __init__(self, ctx: commands.Context, pages: list, starting_page=0, time_limit=10, loop=None):
        self.ctx = ctx      # context taken from command
        self.pages = pages  # pages to display in a list
        self.current_page = starting_page if starting_page < len(pages) else 0 # page to start on
        self.time_limit = time_limit  # time limit for user interaction; counting is reset after each interaction
        self.loop = loop if loop else ctx.bot.loop  # event loop which will be used for the pagination

    async def _handle_message(self):
        """Function handles the reaction events taken from users"""

        page = self.pages[self.current_page]
        msg = await self.ctx.send(page)

        emoji_list = ['⬅️', '➡️', '⏹️']  # These buttons we use
        
        # Predicate
        def check(reaction: discord.Reaction, user):
            return reaction.message.id == msg.id and user == self.ctx.message.author and str(reaction.emoji) in emoji_list

        await self._create_emoji(msg, emoji_list)  # add emoji to message
        
        # Loop that checks for reactions
        while True:
            try:
                # returns a tuple (reaction, user), we just need reaction
                reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.time_limit, check=check)
                emoji = reaction.emoji

                if emoji == '⬅️': # BACK
                    if self.current_page == 0:
                        self.current_page = len(self.pages)
                    self.current_page = self.current_page -1 # go back
                    await msg.remove_reaction('⬅️', user)

                elif emoji == '➡️': # FORWARD
                    self.current_page = self.current_page +1 # go forwards
                    if self.current_page == len(self.pages):
                        self.current_page = 0
                    await msg.remove_reaction('➡️', user)

                elif emoji == '⏹️': # STOP REACTIONS
                    return await self._clear_emoji(msg, emoji_list)

                new_content = "{}/{} {}".format((self.current_page+1), len(self.pages), self.pages[self.current_page])
                await msg.edit(content=new_content)

            except asyncio.TimeoutError:
                return await self._clear_emoji(msg, emoji_list)
    

    async def _clear_emoji(self, msg: discord.Message, emoji_list: list):
        """Fill the mesage with reaction menu"""
        try:
            for reaction in emoji_list:
                await msg.clear_reaction(reaction)
        except Exception:
            return


    async def _create_emoji(self, msg: discord.Message, emoji_list: list):
        """Remove the reaction menu"""
        try:
            for reaction in emoji_list:
                await msg.add_reaction(reaction)
        except Exception:
            return
    

    def create_task(self):
        """Create task in the event loop"""
        self.loop.create_task(self._handle_message())