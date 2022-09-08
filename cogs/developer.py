from typing import Dict
import discord
from utils.database import db
from discord.ext import commands

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def block(self, ctx):
        await ctx.send("Please enter the user id.")
        def check(m):
            return m.content and m.channel
        msg = await self.bot.wait_for("message", check=check, timeout=60)
        if not msg:
            await ctx.send("No message found")
            return
        await db.blocked.insert_one({'_id': msg.content})
        await ctx.send("User blocked successfully.")

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def unblock(self, ctx):
        await ctx.send("Please enter the user id.")
        def check(m):
            return m.content and m.channel
        msg = await self.bot.wait_for("message", check=check, timeout=60)
        if not msg:
            await ctx.send("No message found")
            return
        await db.blocked.delete_one({'_id': msg.content})
        await ctx.send("User unblocked successfully.")
            
async def setup(bot):
    await bot.add_cog(Developer(bot))