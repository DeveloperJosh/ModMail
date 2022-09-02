from typing import Dict
import discord
from utils.database import db
from discord.ext import commands
from utils.dropdown import ServersDropdown, ServersDropdownView, Confirm
from utils.exceptions import DMsDisabled, TicketCategoryNotFound

dropdown_concurrency = []

class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # mod mail
        if message.author.bot:
            return
        if message.channel.type == discord.ChannelType.private:
            if not await db.users.find_one({'_id': message.author.id}):

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
                if not await db.servers.find_one({'_id': guild.id}):
                        embed = discord.Embed(
                            title="Oh no!",
                            description=f"Oh no! The server {guild.name} is not in the database. Please contact a server admin.",
                            color=discord.Color.red()
                        )
                        await message.author.send(embed=embed)
                        return
                data = await db.servers.find_one({'_id': guild.id})
                channel = await guild.create_text_channel(name=f"ticket-{message.author.id}", category=guild.get_channel(data['category'])) # type: ignore
                await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
                embed = discord.Embed(title="Ticket Open", description=f"You have opened a ticket. Please wait for a staff member to reply.", color=0x00ff00)
                embed.set_footer(text="Modmail")
                await message.author.send(embed=embed)
                embed = discord.Embed(title=f"```User ID: {message.author.id}```", color=discord.Color.blurple())
                time = message.author.created_at.strftime("%b %d, %Y")
                embed.add_field(name="User Name", value=message.author.name, inline=False)
                embed.add_field(name="Account Age", value=f"{time}", inline=False)
                embed.add_field(name="Message", value=f"{message.content}", inline=True)
                embed.set_footer(text="Modmail")
                await db.users.insert_one({'_id': message.author.id, "ticket": channel.id, "guild": guild.id})
                role = await db.servers.find_one({'_id': guild.id})
                await channel.send(f"<@&{role['staff_role']}>")
                files = [await attachment.to_file() for attachment in message.attachments]
                if len(files) > 1:
                    await channel.send(content=files)
                await channel.send(embed=embed)
                await channel.create_webhook(name=message.author.name)

            else:
                data = await db.users.find_one({'_id': message.author.id})
                guild = self.bot.get_guild(data['guild']) # type: ignore
                channel = guild.get_channel(data['ticket']) # type: ignore
                webhook_in_channel = await channel.webhooks()
                webhook = webhook_in_channel[0]
                files = [await attachment.to_file() for attachment in message.attachments]
                await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar.url, files=files)


    @commands.hybrid_command()
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=True)

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def reply(self, ctx: commands.Context, *, message):
        msg = await ctx.send("Send reply", ephemeral=True)
        ticket_id = ctx.channel.id
        data = await db.users.find_one({'ticket': ticket_id})
        user_id = data['_id'] # type: ignore
        # dm the user with the message
        user = self.bot.get_user(user_id)
        #embed = discord.Embed().set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url).set_footer(text=f"Server: {ctx.guild.name}") # type: ignore
        embed = discord.Embed(description=f"**{message}**", color=0x00ff00)
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Server: {ctx.guild.name}")
        try:
         await user.send(
         files=[await attachment.to_file() for attachment in ctx.message.attachments],
         embed=embed)
         webhook = await ctx.channel.webhooks()  # type: ignore
         await webhook[0].send(message, username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
        except:
            raise DMsDisabled(user)
        if ctx.message is None:
            return
        else:
            await ctx.message.delete()
            await msg.delete()

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def areply(self, ctx, *, message):
        msg = await ctx.send("Send reply", ephemeral=True)
        ticket_id = ctx.channel.id
        data = await db.users.find_one({'ticket': ticket_id})
        user_id = data['_id'] # type: ignore
        # dm the user with the message
        user = self.bot.get_user(user_id)
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
         await db.users.delete_one({'ticket': ctx.channel.id})
         embed = discord.Embed(title="Ticket Closed", description=f"Your ticket has been closed", color=0x00ff00)
         embed.set_footer(text="Modmail")
         user = self.bot.get_user(int(id))
         await user.send(embed=embed)
         await ctx.message.channel.delete()
        else:
         id = ctx.message.channel.name.split("-")[1]
         await db.users.delete_one({'ticket': ctx.channel.id})
         embed = discord.Embed(title="Ticket Closed", description=f"Your ticket has been closed\nReason: {reason}", color=0x00ff00)
         embed.set_footer(text="Modmail")
         user = self.bot.get_user(int(id))
         await user.send(embed=embed)
         await ctx.message.channel.delete()

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        if not await db.servers.find_one({'_id': ctx.guild.id}):
             category = await ctx.guild.create_category(name="Tickets")
             role = await ctx.guild.create_role(name="Ticket Support")
             if role.position >= ctx.guild.me.top_role.position:
              return await ctx.send("Please give me a higher role position")
             await db.servers.insert_one({'_id': ctx.guild.id, 'category': category.id, "staff_role": role.id})
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
            await db.servers.delete_one({'_id': ctx.guild.id})
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

    @commands.group(invoke_without_command=False)
    @commands.guild_only()
    async def snippet(self, ctx):
        pass

    @snippet.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Help", description="```\nsnippet set [name] ['text']\nsnippet use [name]```", color=0x00ff00)
        await ctx.send(embed=embed)

    @snippet.command()
    async def set(self, ctx):
     stuff = {}
     await ctx.send("Please enter the name of the tag")
     def check(m):
        return m.content and m.channel

     msg = await self.bot.wait_for("message", check=check, timeout=60)
     if not msg:
        await ctx.send("No message found")
        return
     stuff.update({"guild": ctx.guild.id, "command": msg.content})
     await ctx.send("Please enter what this tag will say.")
     def check_tag(m):
        return m.content and m.channel
     msg_tag = await self.bot.wait_for("message", check=check_tag, timeout=60)
     if not msg_tag:
        await ctx.send("No message found")
        return
     stuff.update({"text": msg_tag.content})
     await db.commands.insert_one({**stuff})
     await ctx.send("Tag set successfully.")

    @snippet.command()
    async def use(self, ctx, name):
        if name is None:
            await ctx.send("Please enter a command name.")
        else:
           try:
            command = await db.commands.find_one({"guild": ctx.guild.id, "command": name})
            text = command["text"]
            ticket_id = ctx.channel.id
            data = await db.users.find_one({'ticket': ticket_id})
            user_id = data['_id'] # type: ignore
            user = self.bot.get_user(user_id)
            embed = discord.Embed(title="Ticket Reply", description=f"**{text}**", color=0x00ff00)
            embed.set_footer(text=f"Server: {ctx.guild.name}")
            await user.send(embed=embed)
            webhook = await ctx.channel.webhooks()  # type: ignore
            await webhook[0].send(text, username=ctx.author.name, avatar_url=ctx.author.avatar.url) # type: ignore
           except:
            await ctx.send(f"It looks like the command {name} is not working or does not exist.")

            
async def setup(bot):
    await bot.add_cog(Modmail(bot))