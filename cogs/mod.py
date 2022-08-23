from email import message
import discord
from discord.ext import commands
from utils.database import db

class Mod_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = 1009594348993781801
        self.staff = 1010992361662316645

    @commands.command()
    @commands.is_owner()
    async def ban(self, ctx, user: discord.Member, *, reason):
        if user is ctx.message.author:
           embed = discord.Embed(title="No!!", description="You can not ban yourself")
           await ctx.send(embed=embed)
           return
        else:
            embed = discord.Embed(title="Banned", description=reason)
            await ctx.send(embed=embed)
            await user.send(embed=embed)
            user.ban(reason)


async def setup(bot):
    await bot.add_cog(Mod_Commands(bot))