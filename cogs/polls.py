import discord

from discord.ext import commands

class Poll:
    def __init__(self, name):
        self.name = name
        self.options = []
        self.votes = {}

    def add_option(self, option: str):
        self.options.append(option)

    def number_options(self):
        return len(self.options)

    def add_vote(self, user_id, option_num: int):
        if option_num >= len(self.options):
            raise Exception("Tried to vote out of bounds")
        self.votes[user_id] = option_num
        
    def check_if_voted(self, user_id):
        return user_id in self.votes


class Polls(commands.Cog):
    """
    This cog is responsible for providing a poll feature.
    Every discord has single slot for a poll users can vote in.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.polls = {}

    @commands.command()
    async def createpoll(self, ctx: commands.Context, name: str, *options):
        if ctx.guild.id in self.polls:
            return await ctx.send("ERROR: Poll already exists for this server: %s" % self.polls[ctx.guild.id].name)

        if len(options) < 2:
            return await ctx.send("ERROR: Poll has to have at least 2 choices.\nExample: ,createpoll \"What is your favorite color?\" Yellow \"Light blue\"")

        new_poll = Poll(name)
        self.polls[ctx.guild.id] = new_poll
        for option in options:
            new_poll.add_option(option)

        await ctx.send("Created a new poll: %s" % name)

    @commands.command()
    async def votepoll(self, ctx: commands.Context, option: str):
        vote = 0
        try:
            vote = int(option)
        except Exception:
            return await ctx.send("ERROR: Please vote by providing a number of an option")

        poll = self.polls[ctx.guild.id]
        if poll.number_options() < vote or vote <= 0:
            return await ctx.send("ERROR: Wrong option number, there are only %i available options" % poll.number_options())
        
        vote_idx = vote - 1 # starts at 0
        poll.add_vote(ctx.author.id, vote_idx)
        await ctx.send("You voted for option %i" % vote)

    
    @commands.command()
    async def deletepoll(self, ctx: commands.Context):
        poll_name = self.polls[ctx.guild.id].name
        del self.polls[ctx.guild.id]
        await ctx.send("Deleted poll \"%s\"" % poll_name)

    @commands.command()
    async def showpoll(self, ctx: commands.Context):
        poll: Poll = self.polls[ctx.guild.id]  # grab the poll in question
        
        results = [0] * poll.number_options()  # storage for results, index is option

        for key in poll.votes:
            vote = poll.votes[key]
            results[vote] = results[vote] + 1

        string = "**%s** results:" % poll.name

        i = 1
        for option in poll.options:
            string = string + ("\n%i. " % i )
            string = string + str(option)
            string = string + (":\t%i" % results[i-1])
            i = i + 1

        await ctx.send(string)

    @votepoll.before_invoke
    @deletepoll.before_invoke
    @showpoll.before_invoke
    async def ensure_poll_existence(self, ctx):
        """Make sure that the pool exists"""
        
        if not ctx.guild.id in self.polls:
            return await ctx.send("ERROR: There are no polls in this discord at the moment. Please create new one first `,createpoll`")


def setup(bot):
    bot.add_cog(Polls(bot))