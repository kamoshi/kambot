"""
Commands in this module:
 - hi
 - TODO: pfp
 - TODO: info
"""
import time
import discord
from discord.ext import commands

class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx):
        await ctx.send("Hello, %s!" % ctx.author.name)

    @commands.command()
    async def info(self, ctx):
        """Display information about this bot"""

        def humanize_time(secs):
            mins, secs = divmod(secs, 60)
            hours, mins = divmod(mins, 60)
            return '%02d:%02d:%02d' % (hours, mins, secs)

        embed = discord.Embed(
            title=self.bot.user.name,
            color=discord.Color.blurple()
        )
        embed.add_field(name="Uptime", value=humanize_time(int(time.time()-self.bot.init_time)), inline=True)
        embed.add_field(name="Latency", value="{} ms".format(int(self.bot.latency*100)), inline=True)
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Github", value="https://github.com/kamoshi/kambot", inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["guild"])
    async def server(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        embed=discord.Embed(
            title=guild.name
        )
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Members", value=guild.member_count)
        await ctx.send(embed=embed)

        

    @commands.command(aliases=["pfp"])
    async def avatar(self, ctx: commands.Context, *, arg: discord.Member):
        embed: discord.Embed = discord.Embed(
            color=discord.Color.blurple(),
            description="[link]({})".format(arg.avatar_url),
            title="{}'s avatar".format(arg.display_name)
        )
        embed.set_image(url=arg.avatar_url)
        await ctx.send(embed=embed)


    # MOD COMMANDS

    @commands.command(aliases=["roles"])
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, *role_names: tuple):
        if not member:
            return await ctx.send("Couldn't find any member with this nickname")
        
        member_roles = member.roles
        string = "{}: ".format(member.display_name)
        for role_name in role_names:
            role = discord.utils.get(ctx.guild.roles, name=''.join(role_name))
            if role in member_roles:
                await member.remove_roles(role)
                string += "-{} ".format(role.name)
            else:
                await member.add_roles(role)
                string += "+{} ".format(role.name)

        await ctx.send(string)


    # OWNER COMMANDS

    @commands.is_owner()
    @commands.command(hidden=True)
    async def botstatus(self, ctx: commands.Context, *, new_status: str):
        activity=discord.Activity(name=new_status, type=discord.ActivityType.playing)
        await self.bot.change_presence(activity=activity)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def botname(self, ctx: commands.Context, *, new_name: str):
        await self.bot.user.edit(username=new_name)


def setup(bot):
    bot.add_cog(Core(bot))