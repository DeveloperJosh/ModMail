from typing import Dict
import discord
from utils.db import Database
from discord.ext import commands
from utils.embed import custom_embed, error_embed, success_embed, image_embed
from handler.bot import Bot

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.bot_stuff = Bot(bot)
    
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

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def info(self, ctx, id):
        data = await self.bot_stuff.user_data(id)
        if not data:
            embed = error_embed("Error", "This user is not in the database\nI'm going to try to add them now")
            return await ctx.send(embed=embed)
        embed = custom_embed("User Info", f"Name: {data['name']}#{data['discriminator']}\nID: {id}\nAvatar: [Click Here]({data['avatar']})")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def log(self, ctx, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        for member in guild.members:
            if not await self.bot_stuff.user_data(member.id):
                await self.bot_stuff.user_data(member.id)
            
async def setup(bot):
    await bot.add_cog(Developer(bot))