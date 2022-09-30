import discord
from discord.ext import commands
from utils.db import Database

## TODO: Clean the code, add more comments, and add more features, make it much more user friendly

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()


    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Config", description=f"This is a beta command but here are the sub commands\ncategory <id>\nrole <id>", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)

    @config.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def category(self, ctx, id):
        # get category from id
        if not await self.db.find_server(ctx.guild.id):
            return await ctx.send("Please run `setup` first")
        await self.db.update_server(ctx.guild.id, {'category': int(id)})
        category = discord.utils.get(ctx.guild.categories, id=int(id))
        embed = discord.Embed(title="Category Updated", description=f"The category has been updated to {category}", color=0x00ff00)
        embed.set_footer(text="Modmail")
        await ctx.send(embed=embed)

    @config.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def role(self, ctx, role: discord.Role):
        if not await self.db.find_server(ctx.guild.id):
            return await ctx.send("Please run `setup` first")
        await self.db.update_server(ctx.guild.id, {'staff_role': role.id})
        embed = discord.Embed(title="Staff Role Updated", description=f"The staff role has been updated to {role.name}", color=0x00ff00)
        embed.set_footer(text="Modmail")
        await ctx.send(embed=embed)

    @config.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def transcript(self, ctx, channel: discord.TextChannel):
        if not await self.db.find_server(ctx.guild.id):
            return await ctx.send("Please run `setup` first")
        await self.db.update_server(ctx.guild.id, {'transcript_channel': channel.id})
        embed = discord.Embed(title="Transcript Channel Updated", description=f"The transcript channel has been updated to {channel.mention}", color=0x00ff00)
        embed.set_footer(text="Modmail")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Config(bot))