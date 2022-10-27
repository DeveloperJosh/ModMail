import logging
import sys
import traceback
from typing import Union
import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions, CheckFailure, CommandNotFound, MissingRequiredArgument, BadArgument, MissingRole
from utils.exceptions import (
    NotSetup, NotStaff, NotAdmin, ModRoleNotFound,
    TicketCategoryNotFound, TranscriptChannelNotFound,
    UserAlreadyInAModmailThread, DMsDisabled, NoBots,
    GuildOnlyPls, TicketChannelNotFound
)
from utils.embed import error_embed

class ErrorHandling(commands.Cog, name="on command error"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            day = round(error.retry_after / 86400)
            hour = round(error.retry_after / 3600)
            minute = round(error.retry_after / 60)
            if day > 0:
                await ctx.send('This command has a cooldown, be sure to wait for ' + str(day) + " day(s)")
            elif hour > 0:
                await ctx.send('This command has a cooldown, be sure to wait for ' + str(hour) + " hour(s)")
            elif minute > 0:
                await ctx.send('This command has a cooldown, be sure to wait for ' + str(minute) + " minute(s)")
            else:
                await ctx.send(f'This command has a cooldown, be sure to wait for {error.retry_after:.2f} second(s)')
        elif isinstance(error, CommandNotFound):
            return
        elif isinstance(error, MissingPermissions):
            embed = discord.Embed(title="ERROR!", description=f"{error}")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            perms = error.missing_permissions
            if "embed_links" in perms:
                return await ctx.reply("Please give me embed link perms.")
                # show the name of the missing perms
            embed = error_embed("Missing Permissions", f"{error}")
            await ctx.send(embed=embed)
        elif isinstance(error, MissingRole):
            embed = discord.Embed(title="ERROR!", description=f"{error}")
            await ctx.send(embed=embed)    
        elif isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(title="ERROR!", description=f"{error}")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(title="Developer Only", description="You must be a developer to run this command")
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(error, CheckFailure):
            return
        elif isinstance(error, BadArgument):
            embed = discord.Embed(title="ERROR!", description=f"{error}")
            await ctx.send(embed=embed)
        elif isinstance(error, TicketCategoryNotFound):
            await ctx.reply(embed=error_embed(
                f"Not Found!",
                "Uh oh! Looks like the ticket category was not found! Maybe the category was deleted.\nPlease use `?setup` to set a new one."
            ))
        elif isinstance(error, TicketChannelNotFound):
            await ctx.reply(embed=error_embed(
                f"Not Found!",
                "Uh oh! Looks like the ticket channel was not found! Maybe the channel was deleted.\nPlease use Join the support server to get help.\nhttps://discord.gg/MsPSSvKFfn"
            ))
        elif isinstance(error, DMsDisabled):
            await ctx.reply(embed=error_embed(
                f"Unable to DM!",
                f"I am unable to dm {error.user} because their DMs are disabled.\nPlease ask them to enable their DMs."
            ))
        elif isinstance(error, NoBots):
            await ctx.reply(embed=error_embed(
                "Bots are not allowed!",
                "Bots are not allowed to create tickets."
            ))
        else:
            logging.error(f"Error in command {ctx.command}: {error}")
            e = traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            embed = discord.Embed(title="Unknown Error!", description=f"```{error}```", color=discord.Color.red())
            channel = self.bot.get_channel(889115230355996703)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ErrorHandling(bot=bot))