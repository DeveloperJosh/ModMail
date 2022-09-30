import time
from typing import Dict
import discord
from utils.db import Database
from discord.ext import commands
from utils.dropdown import ServersDropdown, ServersDropdownView, Confirm
from utils.exceptions import DMsDisabled, TicketCategoryNotFound
from utils.embed import custom_embed, error_embed, success_embed
from utils.ticket_core import Ticket

dropdown_concurrency = []

class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.ticket = Ticket(bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        # mod mail
        if message.author.bot:
            return
        if message.channel.type == discord.ChannelType.private:
            if await self.db.is_blocked_list(message.author.id):
                await message.channel.send("You are blocked from using this bot.", delete_after=5)
                print(f"{message.author} tried to use the bot but is blocked.")
                return
            if not await self.db.find_user(message.author.id):
              mutual_guilds = message.author.mutual_guilds
              final_mutual_guilds: Dict[discord.Guild, dict] = {}
              for guild in mutual_guilds:
               try:
                    final_mutual_guilds.update({guild: guild.id})
               except:
                print("Could not find guild: {}".format(guild))
                return
              view = ServersDropdownView()
              select = ServersDropdown(list(final_mutual_guilds))
              view.add_item(select)
              main_msg = await message.channel.send("Hey looks like you want to start a modmail thread.\nIf so, please select a server you want to contact and continue.\nNote you have to hit confirm.", view=view)
              dropdown_concurrency.append(message.author.id)
              await view.wait()
              if not view.yes:
                    return await main_msg.delete()
              final_guild = self.bot.get_guild(int(view.children[2].values[0]))  # type: ignore
              await main_msg.edit(view=None)
              confirm = Confirm(message, 60)
              m = await message.channel.send(f"Are you sure you want to send this message to {final_guild.name}'s staff?", view=confirm)
              await confirm.wait()
              if not confirm.value:
                return await m.delete()
              await m.edit(view=None)
              if message.author.id in dropdown_concurrency:
                dropdown_concurrency.remove(message.author.id)
                await main_msg.delete()
                await m.delete()
                guild = self.bot.get_guild(int(view.children[2].values[0]))  # type: ignore
                if not await self.db.find_server(guild.id):
                        embed = discord.Embed(
                            title="Oh no!",
                            description=f"Oh no! The server {guild.name} is not in the database. Please contact a server admin.",
                            color=discord.Color.red()
                        )
                        await message.author.send(embed=embed)
                        return
                try:
                 # Most of this code is from the ticket core ./utils/ticket_core.py
                 await self.ticket.create(message.author.id, guild.id, message)
                except Exception as e:
                    print(e)
                    await message.author.send(embed=error_embed("Oh no!", "Something went wrong while creating your ticket. Please try again later."))
            else:
               try:
                data = await self.db.find_user(message.author.id)
                guild = self.bot.get_guild(data['guild']) # type: ignore
                channel = guild.get_channel(data['ticket']) # type: ignore
                await self.ticket.send_mondmail_message(channel, message, message.author.name)
               except Exception as e:
                print(e)
                await message.channel.send("An error occured. Please try again later.")


    @commands.hybrid_command()
    @commands.guild_only()
    async def ping(self, ctx, number=1):
       try:
        msg = await ctx.send("Pinging...")
        db_ping = await self.db.add_user(number, {"ping": "pong"})
        start = time.perf_counter()
        db_ping = await self.db.delete_user(number)
        stop = time.perf_counter()
        db_ping = round((stop - start) * 1000)
        bot_ping = self.bot.latency

        bot_ping = round(bot_ping * 1000)
        embed = custom_embed("Ping:ping_pong:", f"DB Ping: {db_ping}ms\nBot Ping: {bot_ping}ms")
        await msg.edit(content=None, embed=embed)
       except Exception as e:
        await ctx.send(e)
        print(e)


    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def reply(self, ctx: commands.Context, *, message):
        try:
            data = await self.db.find_ticket_user(ctx.channel.id)
            id = data['_id'] # type: ignore
        except:
            return await ctx.send("This is not a ticket channel.")
        user = self.bot.get_user(int(id))
        if not await self.ticket.check(int(id)):
            await ctx.send("This is not a ticket channel.", ephemeral=True)
            return
        d = await ctx.send("Send reply", ephemeral=True)
        embed = discord.Embed(description=f"**{message}**", color=0x00ff00)
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Server: {ctx.guild.name}") # type: ignore
        try:
         await user.send(embed=embed)
         await d.delete()
         webhook = await ctx.channel.webhooks()  # type: ignore
         await webhook[0].send(message, username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
        except Exception as e:
            print(e)
            raise DMsDisabled(user)
        

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def areply(self, ctx, *, message):
        msg = await ctx.send("Send reply", ephemeral=True)
        id = ctx.channel.name.split("-")[1]  # type: ignore
        user = self.bot.get_user(int(id))
        embed = discord.Embed(title="Ticket Reply", description=f"**{message}**", color=0x00ff00)
        embed.set_footer(text=f"Server: {ctx.guild.name}")
        await user.send(
        files=[await attachment.to_file() for attachment in ctx.message.attachments],
        embed=embed)
        webhook = await ctx.channel.webhooks()  # type: ignore
        await webhook[0].send(message, username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
        if ctx.message is None:
            return
        else:
            await ctx.message.delete()
            await msg.delete()

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def close(self, ctx, *, reason=None):
        if reason is None:
         id = ctx.message.channel.name.split("-")[1]
         user = self.bot.get_user(int(id))
         await self.db.delete_user(user.id)
         embed = discord.Embed(title="Ticket Closed", description=f"Your ticket has been closed", color=0x00ff00)
         embed.set_footer(text="Modmail")
         await user.send(embed=embed)
         await ctx.message.channel.delete()
        else:
         id = ctx.message.channel.name.split("-")[1]
         user = self.bot.get_user(int(id))
         await self.db.delete_user(user.id)
         embed = discord.Embed(title="Ticket Closed", description=f"Your ticket has been closed\nReason: {reason}", color=0x00ff00)
         embed.set_footer(text="Modmail")
         await user.send(embed=embed)
         await ctx.message.channel.delete()

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        if not await self.db.find_server(ctx.guild.id):
             category = await ctx.guild.create_category(name="Tickets")
             role = await ctx.guild.create_role(name="Ticket Support")
             if role.position >= ctx.guild.me.top_role.position:
              return await ctx.send("Please give me a higher role position")
             await self.db.create_server(ctx.guild.id, {'category': category.id, "staff_role": role.id})
             embed = discord.Embed(title="Setup", description=f"Okay I know you didn't get to pick this stuff but that is coming soon\nCategory: {category.name}\nSupport Role: {role.name}", color=0x00ff00)
             embed.set_footer(text="Modmail")
             await ctx.send(embed=embed)
             await category.set_permissions(ctx.guild.me, read_messages=True, send_messages=True)
             await category.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
             await category.set_permissions(ctx.guild.get_role(role.id), read_messages=True, send_messages=True)
        else:
            embed = discord.Embed(title="Setup Complete", description=f"The server {ctx.guild.name} has already been setup.", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        try:
            embed = discord.Embed(title="Reset", description="Everything We had on your server has been deleted.", color=0x00ff00)
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)
            await self.db.delete_server(ctx.guild.id)
        except:
            embed = discord.Embed(title="Error:x:",
            description="The server is not setup.", color=discord.Color.red())
            embed.set_footer(text="Modmail")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
     await self.bot.reload_extension(f"cogs.{extension}")
     embed = discord.Embed(title='Reload', description=f'{extension} successfully reloaded', color=0xff00c8)
     await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
     await self.bot.reload_extension(f"cogs.{extension}")
     embed = discord.Embed(title='loaded', description=f'{extension} successfully loaded', color=0xff00c8)
     await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.guild_only()
    async def help(self, ctx):
        embed = discord.Embed(title="Modmail", description="Modmail is a bot that allows you to send messages to staff members in DMs.", color=0x00ff00)
        embed.add_field(name="Commands", value="""
```
ping - pong
reply [message] - reply to a ticket
areply [message] - reply anonymously to a ticket
close [reason] - close a ticket
help - this help message
setup - sets up the server
reset - removes all data from the db
snippet [set, help, use] - Allows you to send preset messages
config [category, role] - Allows you to change the config
```""", inline=False)
        embed.set_footer(text="Modmail")
        await ctx.send(embed=embed)
            
async def setup(bot):
    await bot.add_cog(Modmail(bot))