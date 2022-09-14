from typing import Dict
import discord
from utils.db import Database
from discord.ext import commands

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def block(self, ctx, id: str):
        try:
            if await self.db.is_blocked(id):
                await ctx.send("User is already blocked")
                return
            else:
                await self.db.block(id)
                await ctx.send("User has been blocked")
                return
        except Exception as e:
            await ctx.send(e)
            print(e)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def unblock(self, ctx, id):
        try:
            if await self.db.is_blocked(id):
                await self.db.unblock(id)
                await ctx.send("User has been unblocked")
                return
            else:
                await ctx.send("User is not blocked")
                return
        except Exception as e:
            await ctx.send(e)
            print(e)
            
async def setup(bot):
    await bot.add_cog(Developer(bot))