import discord
from discord.ext import commands
from utils.db import Database
from utils.embed import Embed, error_embed
from utils.dropdown import RolesDropdown, RolesDropdownView, CategoryDropdown, CategoryDropdownView, ChannelsDropdown, ChannelsDropdownView


## TODO: Clean the code, add more comments, and add more features, make it much more user friendly

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.hybrid_command(help="Configure the bot", aliases=['c'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def config(self, ctx):
        # show the config menu like a help command
        server_settings = await self.db.find_server(ctx.guild.id)
        if not server_settings:
            # send an error embed
            await ctx.send(embed=error_embed("Error:x:", "This server is not setup yet, please use `?setup` to setup the server"))
            return
        # send the config settings
        embed = Embed(title="Config", description="Here are the current config settings for this server\n\nTo edit the config run `?edit-config [setting]`", color=0x00ff00)
        category = discord.utils.get(ctx.guild.categories, id=server_settings["category"])
        embed.add_field(name="Category", value=category.mention)
        transcripts = discord.utils.get(ctx.guild.text_channels, id=server_settings["transcript_channel"])
        embed.add_field(name="Transcripts", value=transcripts.mention)
        role = discord.utils.get(ctx.guild.roles, id=server_settings["staff_role"])
        embed.add_field(name="Role", value=role.mention)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="edit-config", help="Edit the config settings", aliases=['ec'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def edit_config(self, ctx, setting=None, *, value=None):
        if setting == "role":
          if value is None:
            roles = [role for role in ctx.guild.roles if role.name != "@everyone"]
            view = RolesDropdownView()
            view.add_item(RolesDropdown(roles))
            try:
             edit_me = await ctx.send(embed=Embed(title="Config", description="Please select a role to start a modmail thread with.", color=0x00ff00), view=view)
             await view.wait()
             if view.yes:
                role = discord.utils.get(ctx.guild.roles, id=int(view.children[2].values[0]))
                await self.db.update_server(ctx.guild.id, {"staff_role": role.id})
                await edit_me.edit(embed=Embed(title="Config", description=f"Successfully set the staff role to {role.mention}", color=0x00ff00), view=None)
             else:
                await edit_me.edit(embed=Embed(title="Config", description="Cancelled", color=0x00ff00), view=None)
            except Exception as e:
                print(e)
                error = error_embed("Error:x:", f"It seems like you may have more then 25 roles, please try `{self.bot.command_prefix}edit-config role [role]`")
                await ctx.send(embed=error)
                return
          else:
               try:
                role = discord.utils.get(ctx.guild.roles, name=value)
                if role is None:
                    await ctx.send(embed=error_embed("Error:x:", "That role does not exist"))
                    return
                await self.db.update_server(ctx.guild.id, {"staff_role": role.id})
                await ctx.send(embed=Embed(title="Config", description=f"Successfully set the staff role to {role.mention}", color=0x00ff00))
               except Exception as e:
                print(e)
                await ctx.send(embed=error_embed("Error:x:", "That role does not exist"))
                return
        elif setting == "category":
            if value is None:
                view = CategoryDropdownView()
                view.add_item(CategoryDropdown(ctx.guild.categories))
                try:
                 edit_me = await ctx.send(embed=Embed(title="Config", description="Please select a category to start a modmail thread with.", color=0x00ff00), view=view)
                 await view.wait()
                 if view.yes:
                    category = discord.utils.get(ctx.guild.categories, id=int(view.children[2].values[0]))
                    await self.db.update_server(ctx.guild.id, {"category": category.id})
                    await edit_me.edit(embed=Embed(title="Config", description=f"Successfully set the category to {category.mention}", color=0x00ff00), view=None)
                 else:
                    await edit_me.edit(embed=Embed(title="Config", description="Cancelled", color=0x00ff00), view=None)
                except Exception as e:
                    print(e)
                    error = error_embed("Error:x:", f"It seems like you may have more then 25 categories, please try `{self.bot.command_prefix}edit-config category [category]\nSorry that you cannot @ping the role.`")
                    await ctx.send(embed=error)
                    return
            else:
                 try:
                    category = discord.utils.get(ctx.guild.categories, name=value)
                    if category is None:
                        await ctx.send(embed=error_embed("Error:x:", "That category does not exist"))
                        return
                    await self.db.update_server(ctx.guild.id, {"category": category.id})
                    await ctx.send(embed=Embed(title="Config", description=f"Successfully set the category to {category.mention}", color=0x00ff00))
                 except Exception as e:
                    print(e)
                    await ctx.send(embed=error_embed("Error:x:", "That category does not exist, try using the category name\nSorry that you cannot #mention the category."))
                    return
        elif setting == "transcripts":
            if value is None:
                view = ChannelsDropdownView()
                view.add_item(ChannelsDropdown(ctx.guild.text_channels))
                try:
                 edit_me = await ctx.send(embed=Embed(title="Config", description="Please select a text channel to send transcripts to.", color=0x00ff00), view=view)
                 await view.wait()
                 if view.yes:
                    channel = discord.utils.get(ctx.guild.text_channels, id=int(view.children[2].values[0]))
                    await self.db.update_server(ctx.guild.id, {"transcript_channel": channel.id})
                    await edit_me.edit(embed=Embed(title="Config", description=f"Successfully set the transcript channel to {channel.mention}", color=0x00ff00), view=None)
                 else:
                    await edit_me.edit(embed=Embed(title="Config", description="Cancelled", color=0x00ff00), view=None)
                except Exception as e:
                    print(e)
                    error = error_embed("Error:x:", f"It seems like you may have more then 25 text channels, please try `{self.bot.command_prefix}edit-config transcripts [channel].\nSorry that you cannot #mention the channel.`")
                    await ctx.send(embed=error)
                    return
            else:
                 try:
                    channel = discord.utils.get(ctx.guild.text_channels, name=value)
                    if channel is None:
                        await ctx.send(embed=error_embed("Error:x:", "That channel does not exist"))
                        return
                    await self.db.update_server(ctx.guild.id, {"transcript_channel": channel.id})
                    await ctx.send(embed=Embed(title="Config", description=f"Successfully set the transcript channel to {channel.mention}", color=0x00ff00))
                 except Exception as e:
                    print(e)
                    await ctx.send(embed=error_embed("Error:x:", "That channel does not exist, try using the channel name"))
                    return
        elif setting == "help":
            embed = Embed(title="Config", description=f"This command is used to edit the config of the bot.\n\n**Usage:**\n`{self.bot.command_prefix}edit-config [setting] [value]`\n\n**Settings:**\n`role` - The role that can start a modmail thread.\n`category` - The category that modmail threads will be created in.\n`transcripts` - The channel that transcripts will be sent to.\n\nNote you can use slash commands here", color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Config", description=f"This command is used to edit the config of the bot.\n\n**Usage:**\n`{self.bot.command_prefix}edit-config [setting] [value]`\n\n**Settings:**\n`role` - The role that can start a modmail thread.\n`category` - The category that modmail threads will be created in.\n`transcripts` - The channel that transcripts will be sent to.\n\nNote you can use slash commands here", color=0x00ff00)
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Config(bot))