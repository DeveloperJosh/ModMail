from typing import Dict
import discord
from utils.db import Database
from discord.ext import commands
from utils.embed import custom_embed, error_embed, success_embed, image_embed

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
                embed = error_embed("Error", "This user is already blocked")
                return await ctx.send(embed=embed)
            else:
                await self.db.block(id)
                embed = success_embed("Success", "This user has been blocked")
                return await ctx.send(embed=embed)
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
                embed = success_embed("Success", "This user has been unblocked")
                return await ctx.send(embed=embed)
            else:
                embed = error_embed("Error", "This user is not blocked")
                return await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
            print(e)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def users(self, ctx):
      users = await self.db.get_users()
      embed = custom_embed("Users", f"Total Users: {len(users)}")
      for user in users:
            embed.add_field(name=user["_id"], value=user["ticket"], inline=False)
      await ctx.send(embed=embed)
            
async def setup(bot):
    await bot.add_cog(Developer(bot))