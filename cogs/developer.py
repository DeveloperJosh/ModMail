from typing import Dict
import discord
from utils.database import db
from discord.ext import commands

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
async def setup(bot):
    await bot.add_cog(Developer(bot))