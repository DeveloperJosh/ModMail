import logging
from typing import Literal
import discord
from discord import app_commands
from discord.ext import commands
from utils.db import Database
from utils.embed import Embed, error_embed


## TODO: Clean the code, add more comments, and add more features, make it much more user friendly

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.hybrid_command(help="Configure the bot", aliases=['c'])
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def config(self, ctx):
        # show the config menu like a help command
        server_settings = await self.db.find_server(ctx.guild.id)
        if not server_settings:
            # send an error embed
            await ctx.send(embed=error_embed("Error:x:", "This server is not setup yet, please use `?setup` to setup the server"))
            return
        # send the config settings
        embed = Embed(title="Config", description="Here are the current config settings for this server\n\nTo edit the config run `/edit-config [setting]`", color=0x00ff00)
        category = discord.utils.get(ctx.guild.categories, id=server_settings["category"])
        embed.add_field(name="Category", value=category, inline=True)
        transcripts = discord.utils.get(ctx.guild.text_channels, id=server_settings["transcript_channel"])
        embed.add_field(name="Transcripts", value=transcripts, inline=True)
        role = discord.utils.get(ctx.guild.roles, id=server_settings["staff_role"])
        embed.add_field(name="Role", value=role, inline=True)
        more_roles = server_settings.get('more_roles')
        if more_roles:
         roles = ""
         for role in more_roles:
            #roles = roles + f"<@&{role}> "
            roles = roles + f"{discord.utils.get(ctx.guild.roles, id=role)}\n"
         embed.add_field(name="More Roles", value=roles, inline=True)
        embed.add_field(
        name="‎",
        value=f"[Github](https://github.com/DeveloperJosh/ModMail) | [Support Server](https://discord.gg/TeSHENet9M) | [Old Bot](https://github.com/DeveloperJosh/MailHook)",
        inline=False
    )
        await ctx.send(embed=embed)

    # app_commands
    @app_commands.command(name="edit-config", description="Edit the config of the bot")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def app_config(self, ctx, role: discord.Role = None, more_roles: discord.Role = None, category: discord.CategoryChannel = None, transcripts: discord.TextChannel = None):  # type: ignore
        if role is not None:
            # check if bot has perms
            if not ctx.guild.me.guild_permissions.manage_roles:
                await ctx.response.send_message(embed=error_embed("Error:x:", "I do not have permission to manage roles"))
                return
            if not await self.db.find_server(ctx.guild.id):
               await ctx.response.send_message(embed=error_embed("Error:x:", "You need to run `/setup` first"))
            try:
             await self.db.update_server(ctx.guild.id, {"staff_role": role.id})
             await ctx.response.send_message(embed=Embed(title="Config", description=f"Successfully set the role to {role.mention}", color=0x00ff00))
            except Exception as e:
                await ctx.response.send_message(embed=error_embed("Error:x:", f"An error occurred: {e}"))
        elif more_roles is not None:
            # check if bot has perms
            if not ctx.guild.me.guild_permissions.manage_roles:
                await ctx.response.send_message(embed=error_embed("Error:x:", "I do not have permission to manage roles"))
                return
            if not await self.db.find_server(ctx.guild.id):
               await ctx.response.send_message(embed=error_embed("Error:x:", "You need to run `/setup` first"))
            try:
             # if there is a role in the list add it to the list using the $push operator
             # check if there is 3 roles in the more_roles list
             data = await self.db.get_server(ctx.guild.id, raise_error=False)
             if len(data["more_roles"]) == 3:
                # send an error embed
                # update number 2 to the new role
                await self.db.update_server(ctx.guild.id, {"more_roles.2": more_roles.id})
                await ctx.response.send_message(embed=Embed(title="Config", description=f"Successfully set the role to {more_roles.mention}", color=0x00ff00))
                return
             await self.db.update_server_list(ctx.guild.id, {"more_roles": more_roles.id})
             await ctx.response.send_message(embed=Embed(title="Config", description=f"Successfully set the role to {more_roles.mention}", color=0x00ff00))
            except Exception as e:
                await ctx.response.send_message(embed=error_embed("Error:x:", f"An error occurred: {e}"))
        elif category is not None:
            if not ctx.guild.me.guild_permissions.manage_channels:
                await ctx.response.send_message(embed=error_embed("Error:x:", "I do not have permission to manage channels"))
                return
            if not await self.db.find_server(ctx.guild.id):
                await ctx.response.send_message(embed=error_embed("Error:x:", "You need to run `/setup` first"))
            await self.db.update_server(ctx.guild.id, {"category": category.id})
            await ctx.response.send_message(embed=Embed(title="Config", description=f"Successfully set the category to {category.mention}", color=0x00ff00))
        elif transcripts is not None:
            if not ctx.guild.me.guild_permissions.manage_channels:
                await ctx.response.send_message(embed=error_embed("Error:x:", "I do not have permission to manage channels"))
                return
            if not await self.db.find_server(ctx.guild.id):
                await ctx.response.send_message(embed=error_embed("Error:x:", "You need to run `/setup` first"))
            await self.db.update_server(ctx.guild.id, {"transcript_channel": transcripts.id})
            await ctx.response.send_message(embed=Embed(title="Config", description=f"Successfully set the transcript channel to {transcripts.mention}", color=0x00ff00))
        # if more then 1 option is not None then send error
        elif role is not None and category is not None and transcripts is not None:
            await ctx.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time"))
        else:
            embed = Embed(title="Config", description=f"This command is used to edit the config of the bot.\n\n**Usage:**\n`/edit-config [setting] [value]`\n\n**Settings:**\n`role` - The role that can start a modmail thread.\n`category` - The category that modmail threads will be created in.\n`transcripts` - The channel that transcripts will be sent to.", color=0x00ff00)
            await ctx.response.send_message(embed=embed)

    @app_config.error  # type: ignore
    async def app_config_error(self, ctx: discord.Integration, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You do not have permission to use this command")) # type: ignore
        elif isinstance(error, discord.app_commands.errors.CommandLimitReached):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time")) # type: ignore
        else:
            logging.error(error)

async def setup(bot):
    await bot.add_cog(Config(bot))