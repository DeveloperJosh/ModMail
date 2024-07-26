import logging
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from utils.db import Database
from utils.embed import Embed, error_embed

class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()

    @commands.hybrid_command(help="Configure the bot", aliases=['c'])
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def config(self, ctx: commands.Context):
        # Fetch server settings from the database
        server_settings = await self.db.find_server(ctx.guild.id)
        if not server_settings:
            # Send an error embed if the server is not set up
            await ctx.send(embed=error_embed("Error:x:", "This server is not setup yet, please use `?setup` to setup the server"))
            return

        # Prepare the config embed
        embed = Embed(title="Config", description="Here are the current config settings for this server\n\nTo edit the config run `/edit-config [setting]`", color=0x00ff00)
        category = discord.utils.get(ctx.guild.categories, id=server_settings["category"])
        embed.add_field(name="Category", value=category, inline=True)
        transcripts = discord.utils.get(ctx.guild.text_channels, id=server_settings["transcript_channel"])
        embed.add_field(name="Transcripts", value=transcripts, inline=True)
        role = discord.utils.get(ctx.guild.roles, id=server_settings["staff_role"])
        embed.add_field(name="Role", value=role, inline=True)

        more_roles = server_settings.get('more_roles')
        if more_roles:
            roles = "\n".join([str(discord.utils.get(ctx.guild.roles, id=role)) for role in more_roles])
            embed.add_field(name="More Roles", value=roles, inline=True)

        embed.add_field(
            name="‎",
            value="[Github](https://github.com/DeveloperJosh/ModMail) | [Support Server](https://discord.gg/TeSHENet9M) | [Old Bot](https://github.com/DeveloperJosh/MailHook)",
            inline=False
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="edit-config", description="Edit the config of the bot")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def app_config(self, interaction: discord.Interaction, role: Optional[discord.Role] = None, more_roles: Optional[discord.Role] = None, category: Optional[discord.CategoryChannel] = None, transcripts: Optional[discord.TextChannel] = None):
        # Check if the server is set up
        if not await self.db.find_server(interaction.guild.id):
            await interaction.response.send_message(embed=error_embed("Error:x:", "You need to run `/setup` first"))
            return

        # Update the server settings based on provided arguments
        if role is not None:
            await self.update_role(interaction, role)
        elif more_roles is not None:
            await self.update_more_roles(interaction, more_roles)
        elif category is not None:
            await self.update_category(interaction, category)
        elif transcripts is not None:
            await self.update_transcripts(interaction, transcripts)
        else:
            # If no valid arguments are provided, show the usage information
            embed = Embed(
                title="Config",
                description="This command is used to edit the config of the bot.\n\n**Usage:**\n`/edit-config [setting] [value]`\n\n**Settings:**\n`role` - The role that can start a modmail thread.\n`category` - The category that modmail threads will be created in.\n`transcripts` - The channel that transcripts will be sent to.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)

    async def update_role(self, interaction: discord.Interaction, role: discord.Role):
        # Check if the bot has permission to manage roles
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message(embed=error_embed("Error:x:", "I do not have permission to manage roles"))
            return

        # Update the staff role in the database
        try:
            await self.db.update_server(interaction.guild.id, {"staff_role": role.id})
            await interaction.response.send_message(embed=Embed(title="Config", description=f"Successfully set the role to {role.mention}", color=0x00ff00))
        except Exception as e:
            await interaction.response.send_message(embed=error_embed("Error:x:", f"An error occurred: {e}"))

    async def update_more_roles(self, interaction: discord.Interaction, more_roles: discord.Role):
        # Check if the bot has permission to manage roles
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message(embed=error_embed("Error:x:", "I do not have permission to manage roles"))
            return

        # Update the more roles list in the database
        try:
            data = await self.db.get_server(interaction.guild.id, raise_error=False)
            if len(data["more_roles"]) == 3:
                await self.db.update_server(interaction.guild.id, {"more_roles.2": more_roles.id})
            else:
                await self.db.update_server_list(interaction.guild.id, {"more_roles": more_roles.id})
            await interaction.response.send_message(embed=Embed(title="Config", description=f"Successfully set the role to {more_roles.mention}", color=0x00ff00))
        except Exception as e:
            await interaction.response.send_message(embed=error_embed("Error:x:", f"An error occurred: {e}"))

    async def update_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        # Check if the bot has permission to manage channels
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message(embed=error_embed("Error:x:", "I do not have permission to manage channels"))
            return

        # Update the category in the database
        await self.db.update_server(interaction.guild.id, {"category": category.id})
        await interaction.response.send_message(embed=Embed(title="Config", description=f"Successfully set the category to {category.mention}", color=0x00ff00))

    async def update_transcripts(self, interaction: discord.Interaction, transcripts: discord.TextChannel):
        # Check if the bot has permission to manage channels
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message(embed=error_embed("Error:x:", "I do not have permission to manage channels"))
            return

        # Update the transcript channel in the database
        await self.db.update_server(interaction.guild.id, {"transcript_channel": transcripts.id})
        await interaction.response.send_message(embed=Embed(title="Config", description=f"Successfully set the transcript channel to {transcripts.mention}", color=0x00ff00))

    @app_config.error
    async def app_config_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(embed=error_embed("Error:x:", "You do not have permission to use this command"))
        elif isinstance(error, app_commands.errors.CommandLimitReached):
            await interaction.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time"))
        else:
            logging.error(error)
            await interaction.response.send_message(embed=error_embed("Error:x:", "An unexpected error occurred"))

async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))
