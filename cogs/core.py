"""
Commands in this module:
 - hi
 - TODO: pfp
 - TODO: info
"""

import discord
from discord.ext import commands

class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx):
        await ctx.send("Hello, %s!" % ctx.author.name)

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