import discord
from discord.ext import commands
from utils.database import db
from utils.config import guild, staff, logs

class Mod_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = guild
        self.staff = staff
        self.logs = logs

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Command {error} not found")
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(f"Argument parsing error: {error}")
        else:
            await ctx.send(error)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        # log the ban to self.logs
        if guild.id == self.guild:
            channel = guild.get_channel(self.logs)
            embed = discord.Embed(title="A user has been banned", description=f"`User: {user.name}`", color=discord.Color.red())
            await channel.send(embed=embed)
        else:
            pass

    @commands.command()
    @commands.is_owner()
    async def ban(self, ctx, user: discord.Member, *, reason):
     try:
      embed = discord.Embed(title="Banned", description=f"Oh No. It looks like you have been banned by {ctx.message.author.name}.\nReason: {reason}\nGuild: {ctx.guild.name}")
      await user.send(embed=embed)
      await ctx.guild.ban(user)
     except:
        embed = discord.Embed(title="Error:x:", description="It looks like a error has occurred.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mod_Commands(bot))