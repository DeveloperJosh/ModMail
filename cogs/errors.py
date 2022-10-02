import logging
import traceback
import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions, CheckFailure, CommandNotFound, MissingRequiredArgument, BadArgument, MissingRole
from utils.exceptions import (
    NotSetup, NotStaff, NotAdmin, ModRoleNotFound,
    TicketCategoryNotFound, TranscriptChannelNotFound,
    UserAlreadyInAModmailThread, DMsDisabled, NoBots,
    GuildOnlyPls
)
from utils.embed import error_embed

def e(title: str, desc: str) -> discord.Embed:
    return discord.Embed(title=title, description=desc, color=discord.Color.red())

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
            await ctx.reply(embed=embed)
        elif isinstance(error, CheckFailure):
            return
        elif isinstance(error, BadArgument):
            embed = discord.Embed(title="ERROR!", description=f"{error}")
            await ctx.send(embed=embed)
        elif isinstance(error, TicketCategoryNotFound):
            await ctx.reply(embed=e(
                f"Not Found!",
                "Uh oh! Looks like the ticket category was not found! Maybe the category was deleted.\nPlease use `?setup` to set a new one."
            ))
        elif isinstance(error, DMsDisabled):
            await ctx.reply(embed=e(
                f"Unable to DM!",
                f"I am unable to dm {error.user} because their DMs are disabled.\nPlease ask them to enable their DMs."
            ))
        else:
            error_text = f"```py {traceback.format_exc()} ```"
            print(error_text)
            try:
                await ctx.reply(embed=error_embed(
                    "An error has occured!",
                    f"```py {error}```"
                ))
                logging.error(error)
            except Exception as e:
                logging.error(e)
                await ctx.channel.send(f"An error occured: \n\n```{error}```")
            try:
                await self.bot.get_channel(889115230355996703).send(embed=e("Unknown Error", f"```py\n{error_text}\n```"))
            except Exception:
                print("Unable to send error to error channel")

async def setup(bot):
    await bot.add_cog(ErrorHandling(bot=bot))