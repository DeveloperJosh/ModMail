import discord
from discord.ext import commands
from utils.db import Database
from utils.ticket_core import Ticket
from discord import app_commands
## TODO: Clean the code, add more comments, and add more features, make it much more user friendly

class Snippets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.ticket = Ticket(bot)
    snippet = app_commands.Group(name="snippet", description="Use this command to add snippets, Use snippets, and delete snippets")

    @snippet.command(name="add", description="Add a snippet")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def snippet_2_add(self, ctx, name: str, content: str, is_embed: bool):
         if await self.ticket.check(ctx.channel.id) is True:
            return await ctx.response.send_message(embed=discord.Embed(title="Error:x:", description="You can not use this command in a ticket channel", color=0x00ff00), ephemeral=True)

         if await self.db.max_commands(ctx.guild.id) is True:
            embed=discord.Embed(title="Error:x:", description="You have reached the maximum amount of commands you can have", color=0x00ff00)
            embed.add_field(name="How to get more", value="You can vote for the bot on top.gg and get 5 more commands (This is coming soon)")
            return await ctx.response.send_message(embed=embed)

         stuff = {}
         stuff["embed"] = is_embed
         stuff['command'] = name
         stuff['text'] = content
         await self.db.create_command(ctx.guild.id, stuff)
         embed=discord.Embed(title="Success:heavy_check_mark:", description=f"You have successfully added a snippet\n\n`Snippet name`: {name}\n`Snippet content`: {content}\n`Is_embed` {is_embed}", color=0x00ff00)
         await ctx.response.send_message(embed=embed)

    @snippet.command(name="remove", description="Remove a snippet")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def snippet_2_remove(self, ctx, name: str):
        try:
         await self.db.delete_command(ctx.guild.id, name)
         await ctx.response.send_message("Snippet deleted")
        except Exception as e:
            await ctx.response.send_message("It seems like that is not a command or something went wrong", ephemeral=True)
            print(e)

    @snippet.command(name="list", description="Show all the snippets")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def snippet_2_list(self, ctx):
            commands = await self.db.find_commands(ctx.guild.id)
            if commands is None:
                return await ctx.response.send_message("There are no snippets", ephemeral=True)
            if len(commands) == 0:
                return await ctx.response.send_message("There are no snippets", ephemeral=True)
            if not commands:
                return await ctx.response.send_message("There are no snippets", ephemeral=True)
            embed = discord.Embed(title="Snippets", description=f"Here are the snippets", color=0x00ff00)
            for command in commands:
                embed.add_field(name=command['command'], value=command['text'], inline=False)
            embed.set_footer(text="Modmail")
            await ctx.response.send_message(embed=embed)

    @snippet.command(name="use", description="Use a snippet, The snippet will be sent to a ticket user")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def snippet_2_send(self, ctx, name: str):
            data = await self.db.find_ticket(ctx.channel.id)
            if not data:
                    return await ctx.response.send_message("This is not a ticket", ephemeral=True)
            try:
                user = await self.bot.fetch_user(data['_id'])  # type: ignore
            except:
                return
            #print(command)
            command = await self.db.find_command(ctx.guild.id, name)
            if command:
                if command['embed'] == True:
                    embed = discord.Embed(title=command['command'], description=command['text'], color=0x00ff00)
                    embed.set_footer(text="Modmail")
                    await user.send(embed=embed)
                    # now send the webhook
                    webhook = await ctx.channel.webhooks()  # type: ignore
                    await webhook[0].send(command["text"], username="Snippet Used", avatar_url=self.bot.user.avatar.url) # type: ignore
                    await ctx.response.send_message("Snippet sent", ephemeral=True)
                else:
                    txt = f"From **{ctx.guild.name}**:\n{command['text']}"
                    await user.send(txt)
                    webhook = await ctx.channel.webhooks()
                    await webhook[0].send(command["text"], username="Snippet Used", avatar_url=self.bot.user.avatar.url) # type: ignore
                    await ctx.response.send_message("Snippet sent", ephemeral=True)
            else:
                await ctx.response.send_message("That is not a command", ephemeral=True)

    @snippet.command(name="edit", description="Edit the text of a snippet")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def snippet_2_edit(self, ctx, name: str, content: str):
     try:
        found = await self.db.find_command(ctx.guild.id, name)
        if found:
         await self.db.update_command(ctx.guild.id, name, content)
         await ctx.response.send_message("Snippet edited")
        else:
            await ctx.response.send_message("That is not a command", ephemeral=True)
     except Exception as e:
        await ctx.response.send_message("It seems like that is not a command or something went wrong")
        print(e)

async def setup(bot):
    await bot.add_cog(Snippets(bot))