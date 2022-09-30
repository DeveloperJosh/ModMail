from unicodedata import name
import discord
from discord.ext import commands
from utils.db import Database
from utils.ticket_core import Ticket
## TODO: Clean the code, add more comments, and add more features, make it much more user friendly

class Snippet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.ticket = Ticket(bot)

    @commands.command(aliases=['s'])
    async def snippet(self, ctx, *, option=None):
        if option is None:
            embed = discord.Embed(title="Snippet", description=f"To use a snippet do `{self.bot.command_prefix}snippet [cmd_name]`\n\nHere are the sub commands\nadd <name> <content>\nremove <name>", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)

        elif option.startswith("add"):
            # start asking for name and content and if it is a embed or not
            stuff = {}
            def check(m):
             return m.content and m.channel
            await ctx.send("Is this a embed? (yes/no)")
            msg = await self.bot.wait_for('message', check=check)
            if msg.content == "yes":
                stuff['embed'] = True
            elif msg.content == "no":
                stuff['embed'] = False
            else:
                return await ctx.send("Please say yes or no")
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
            if data is None:
                    return await ctx.send("This is not a ticket")
            try:
                user = await self.bot.fetch_user(data['_id'])  # type: ignore
            except Exception as e:
                print(e)
                return await ctx.send("User not found")
            if user is None:
                return await ctx.send("User not found 1")
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