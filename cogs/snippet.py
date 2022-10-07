from turtle import title
from unicodedata import name
import discord
from discord.ext import commands
from utils.db import Database
from utils.ticket_core import Ticket
from discord import app_commands
## TODO: Clean the code, add more comments, and add more features, make it much more user friendly

class Snippet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.ticket = Ticket(bot)

    @commands.hybrid_command(aliases=['s'], help="Use this command to add snippets, Use snippets, and delete snippets")
    async def snippet(self, ctx, *, option=None):
        if option is None:
            #embed = discord.Embed(title="Config", description=f"This command is used to edit the config of the bot.\n\n**Usage:**\n`{self.bot.command_prefix}edit-config [setting] [value]`\n\n**Settings:**\n`role` - The role that can start a modmail thread.\n`category` - The category that modmail threads will be created in.\n`transcripts` - The channel that transcripts will be sent to.\n\nNote you can use slash commands here", color=0x00ff00)
            embed = discord.Embed(title="Snippet", description=f"This command is used to add, use, and delete snippets.\n\n**Usage:**\n`{self.bot.command_prefix}snippet [option] [name] [content]`\n\n**Options:**\n`add` - Add a snippet.\n`use` - Use a snippet.\n`delete` - Delete a snippet.\nTo use a snippet just do this `snippet [name of snippet]`.\n\nNote you can use slash commands here", color=0x00ff00)
            await ctx.send(embed=embed)

        elif option.startswith("add"):
            # start asking for name and content and if it is a embed or not
            # check if channel is a ticket channel
            if await self.ticket.check(ctx.channel.id) is True:
                return await ctx.send(embed=discord.Embed(title="Error:x:", description="You can not use this command in a ticket channel", color=0x00ff00))

            if await self.db.max_commands(ctx.guild.id) is True:
                embed=discord.Embed(title="Error:x:", description="You have reached the maximum amount of commands you can have", color=0x00ff00)
                embed.add_field(name="How to get more", value="You can vote for the bot on top.gg and get 5 more commands (This is coming soon)")
                return await ctx.send(embed=embed)

            stuff = {}
            def check(m):
             return m.content and m.channel
            await ctx.send("Is this a embed? (yes/no)")
            msg = await self.bot.wait_for('message', check=check)
            # lower or upper case
            if msg.content.lower() == "yes" or msg.content == "Yes":
                stuff["embed"] = True
            elif msg.content == "no" or msg.content == "No":
                stuff['embed'] = False
            else:
                return await ctx.send("Unknown response")
            await ctx.send("What is the name?")
            msg = await self.bot.wait_for('message', check=check)
            stuff['command'] = msg.content
            await ctx.send("What is the content?")
            msg = await self.bot.wait_for('message', check=check)
            stuff['text'] = msg.content
            await self.db.create_command(ctx.guild.id, stuff)
            await ctx.send("Snippet created")

        elif option.startswith("remove"):
            name = option[7:]
            await self.db.delete_command(ctx.guild.id, name)
            await ctx.send("Snippet deleted")

        elif option.startswith("list"):
            commands = await self.db.find_commands(ctx.guild.id)
            embed = discord.Embed(title="Snippets", description=f"Here are the snippets", color=0x00ff00)
            for command in commands:
                embed.add_field(name=command['command'], value=command['text'], inline=False)
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)
        else:
            # check if it is a command
            command = await self.db.find_command(ctx.guild.id, option)
            data = await self.db.find_ticket(ctx.channel.id)
            if not data:
                    return await ctx.send("This is not a ticket")
            try:
                user = await self.bot.fetch_user(data['_id'])  # type: ignore
            except:
                return
            #print(command)
            if command:
                if command['embed'] == True:
                    embed = discord.Embed(title=command['command'], description=command['text'], color=0x00ff00)
                    embed.set_footer(text="Modmail")
                    await user.send(embed=embed)
                    # now send the webhook
                    webhook = await ctx.channel.webhooks()  # type: ignore
                    await webhook[0].send(command["text"], username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
                else:
                    txt = f"**{ctx.author.name}** in **{ctx.guild.name}**:\n{command['text']}"
                    await user.send(txt)
                    webhook = await ctx.channel.webhooks()  # type: ignore
                    await webhook[0].send(command["text"], username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
            else:
                await ctx.send("That is not a command")
            

async def setup(bot):
    await bot.add_cog(Snippet(bot))